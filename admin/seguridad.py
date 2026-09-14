"""
Autenticación y defensas del panel.

Los usuarios viven en admin/usuarios.json (creados con `python3 admin/usuarios.py`).
No hay registro público: las cuentas se dan de alta a mano desde el servidor.
"""

import os
import json
import time
import hmac
import secrets
import functools
import threading

from flask import session, request, redirect, url_for, abort, g
from werkzeug.security import check_password_hash, generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
USUARIOS_JSON = os.path.join(BASE, "usuarios.json")

# Bloqueo tras varios intentos fallidos.
MAX_INTENTOS = 5
BLOQUEO_SEGUNDOS = 15 * 60
_intentos = {}
_candado = threading.Lock()


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

def cargar_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return {}
    try:
        with open(USUARIOS_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_usuarios(usuarios):
    tmp = USUARIOS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(usuarios, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, USUARIOS_JSON)
    os.chmod(USUARIOS_JSON, 0o600)


def crear_hash(password):
    return generate_password_hash(password, method="scrypt")


def verificar(usuario, password):
    """Devuelve el dict del usuario si las credenciales son correctas."""
    datos = cargar_usuarios().get((usuario or "").strip().lower())
    # Se comprueba el hash aunque el usuario no exista, para que el tiempo de
    # respuesta no revele qué nombres están dados de alta.
    hash_falso = ("scrypt:32768:8:1$" + "x" * 16 + "$" + "0" * 128)
    if not datos:
        check_password_hash(hash_falso, password or "")
        return None
    if not check_password_hash(datos.get("hash", hash_falso), password or ""):
        return None
    return datos


# ---------------------------------------------------------------------------
# Límite de intentos
# ---------------------------------------------------------------------------

def _clave_cliente():
    return request.remote_addr or "desconocido"


def bloqueado():
    """Segundos que faltan para poder reintentar, o 0 si no está bloqueado."""
    with _candado:
        intentos, hasta = _intentos.get(_clave_cliente(), (0, 0))
    restante = int(hasta - time.time())
    return restante if intentos >= MAX_INTENTOS and restante > 0 else 0


def registrar_fallo():
    with _candado:
        clave = _clave_cliente()
        intentos, _ = _intentos.get(clave, (0, 0))
        intentos += 1
        _intentos[clave] = (intentos, time.time() + BLOQUEO_SEGUNDOS)
        # Limpieza de entradas viejas para que el diccionario no crezca sin fin
        ahora = time.time()
        for k in [k for k, (_, h) in _intentos.items() if h < ahora]:
            _intentos.pop(k, None)


def limpiar_fallos():
    with _candado:
        _intentos.pop(_clave_cliente(), None)


# ---------------------------------------------------------------------------
# Sesión
# ---------------------------------------------------------------------------

def iniciar_sesion(usuario, datos):
    session.clear()
    session["usuario"] = usuario
    session["nombre"] = datos.get("nombre", usuario)
    session["csrf"] = secrets.token_urlsafe(32)
    session.permanent = True


def cerrar_sesion():
    session.clear()


def usuario_actual():
    return session.get("usuario")


def login_requerido(vista):
    @functools.wraps(vista)
    def envoltura(*args, **kwargs):
        if not usuario_actual():
            return redirect(url_for("login", siguiente=request.path))
        g.usuario = usuario_actual()
        g.nombre = session.get("nombre", g.usuario)
        return vista(*args, **kwargs)
    return envoltura


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def validar_csrf():
    enviado = request.form.get("csrf") or request.headers.get("X-CSRF-Token", "")
    esperado = session.get("csrf", "")
    if not esperado or not hmac.compare_digest(str(enviado), str(esperado)):
        abort(400, "Token de seguridad inválido. Recargá la página e intentá de nuevo.")


# ---------------------------------------------------------------------------
# Cabeceras
# ---------------------------------------------------------------------------

def aplicar_cabeceras(respuesta):
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    respuesta.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    respuesta.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
    respuesta.headers["Cache-Control"] = "no-store"
    return respuesta
