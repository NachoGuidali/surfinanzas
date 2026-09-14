"""
Formulario de contacto.

Expone un endpoint público (POST /api/contacto) que:

  1. valida los datos,
  2. GUARDA el mensaje en disco (datos/mensajes.jsonl),
  3. recién después intenta mandarlo por mail.

El orden importa: si el SMTP falla, el mensaje ya está guardado y se puede
leer desde el panel. Un formulario que pierde consultas es peor que no tener
formulario.

Si no configurás SMTP, el endpoint igual funciona: guarda todo y avisa en el
log. Podés sumar las credenciales después sin tocar código.
"""

import os
import re
import ssl
import json
import time
import smtplib
import logging
import threading
import datetime

from email.message import EmailMessage

from flask import Blueprint, request, jsonify, current_app

bp = Blueprint("formulario", __name__)
log = logging.getLogger(__name__)

import contenido as _contenido

RAIZ = _contenido.RAIZ
DATOS_DIR = _contenido.DATOS_DIR          # una sola definición, en contenido.py
ARCHIVO = os.path.join(DATOS_DIR, "mensajes.jsonl")

# Cada área tiene su casilla. Lo que no esté en la lista va a la primera.
AREAS = {
    "Consultas generales": "Info@surfinanzas.com.ar",
    "Reclamos": "Reclamos@surfinanzas.com.ar",
    "Gerencia": "Gerencia@surfinanzas.com.ar",
    "Marketing / prensa": "Marketing@surfinanzas.com.ar",
    "Legales": "Legales@surfinanzas.com.ar",
    "Cumplimiento": "Cumplimiento@surfinanzas.com.ar",
    "Administración": "Administracion@surfinanzas.com.ar",
    "Recursos Humanos": "Rrhh@surfinanzas.com.ar",
}
AREA_POR_DEFECTO = "Consultas generales"

RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")

LIMITE_POR_HORA = 5
_envios = {}
_candado = threading.Lock()

MAX = {"nombre": 80, "email": 120, "area": 60, "mensaje": 4000}
MIN = {"nombre": 2, "mensaje": 10}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _limpiar(valor, largo):
    """Recorta, normaliza espacios y saca caracteres de control."""
    texto = str(valor or "").strip()
    texto = texto.replace("\x00", "")
    return texto[:largo]


def _sin_saltos(valor):
    """Para todo lo que vaya en una cabecera de mail: evita inyección."""
    return re.sub(r"[\r\n]+", " ", valor).strip()


def _ip():
    # nginx manda X-Forwarded-For; nos quedamos con el primero.
    reenviado = request.headers.get("X-Forwarded-For", "")
    if reenviado:
        return reenviado.split(",")[0].strip()
    return request.remote_addr or "desconocido"


def _limite_alcanzado():
    ahora = time.time()
    with _candado:
        for k, marcas in list(_envios.items()):
            vigentes = [t for t in marcas if ahora - t < 3600]
            if vigentes:
                _envios[k] = vigentes
            else:
                _envios.pop(k, None)
        return len(_envios.get(_ip(), [])) >= LIMITE_POR_HORA


def _registrar_envio():
    with _candado:
        _envios.setdefault(_ip(), []).append(time.time())


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def guardar(mensaje):
    os.makedirs(DATOS_DIR, exist_ok=True)
    with open(ARCHIVO, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(mensaje, ensure_ascii=False) + "\n")
    try:
        os.chmod(ARCHIVO, 0o600)
    except OSError:
        pass


def leer_mensajes(limite=300):
    """Los más nuevos primero. Ignora líneas corruptas en vez de romper."""
    if not os.path.exists(ARCHIVO):
        return []
    mensajes = []
    with open(ARCHIVO, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            try:
                mensajes.append(json.loads(linea))
            except json.JSONDecodeError:
                continue
    return list(reversed(mensajes))[:limite]


# ---------------------------------------------------------------------------
# Envío por mail
# ---------------------------------------------------------------------------

def _config_smtp():
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        return None
    return {
        "host": host,
        "puerto": int(os.environ.get("SMTP_PUERTO", "587")),
        "usuario": os.environ.get("SMTP_USUARIO", "").strip(),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "desde": os.environ.get("SMTP_DESDE", "").strip() or os.environ.get("SMTP_USUARIO", "").strip(),
        "seguridad": os.environ.get("SMTP_SEGURIDAD", "starttls").strip().lower(),
    }


def enviar_mail(mensaje):
    """Devuelve (ok, detalle). Nunca lanza: el mensaje ya está guardado."""
    cfg = _config_smtp()
    if not cfg:
        return False, "SMTP sin configurar"

    destino = AREAS.get(mensaje["area"], AREAS[AREA_POR_DEFECTO])
    nombre = _sin_saltos(mensaje["nombre"])
    email = _sin_saltos(mensaje["email"])

    msg = EmailMessage()
    msg["Subject"] = _sin_saltos(f"[Web] {mensaje['area']} — {nombre}")
    msg["From"] = cfg["desde"]
    msg["To"] = destino
    if RE_EMAIL.match(email):
        msg["Reply-To"] = email

    msg.set_content(
        f"Nueva consulta desde el formulario de surfinanzas.com.ar\n"
        f"{'-' * 55}\n\n"
        f"Nombre:  {nombre}\n"
        f"Email:   {email}\n"
        f"Área:    {mensaje['area']}\n"
        f"Fecha:   {mensaje['fecha']}\n\n"
        f"Mensaje:\n{mensaje['mensaje']}\n\n"
        f"{'-' * 55}\n"
        f"Podés responderle directamente a este mail.\n"
    )

    try:
        contexto = ssl.create_default_context()
        if cfg["seguridad"] == "ssl":
            servidor = smtplib.SMTP_SSL(cfg["host"], cfg["puerto"], timeout=20, context=contexto)
        else:
            servidor = smtplib.SMTP(cfg["host"], cfg["puerto"], timeout=20)
        with servidor:
            if cfg["seguridad"] == "starttls":
                servidor.starttls(context=contexto)
            if cfg["usuario"]:
                servidor.login(cfg["usuario"], cfg["password"])
            servidor.send_message(msg)
        return True, destino
    except Exception as err:                      # noqa: BLE001 — se registra y sigue
        log.error("No se pudo enviar el mail de contacto: %s", err)
        return False, str(err)


# ---------------------------------------------------------------------------
# Endpoint público
# ---------------------------------------------------------------------------

@bp.route("/api/contacto", methods=["POST"])
def contacto():
    datos = request.get_json(silent=True) or request.form or {}

    # Trampa para bots: es un campo oculto, una persona nunca lo completa.
    if _limpiar(datos.get("sitio"), 100):
        log.info("Formulario descartado por honeypot desde %s", _ip())
        return jsonify({"ok": True})          # al bot le decimos que salió bien

    if _limite_alcanzado():
        return jsonify({
            "ok": False,
            "error": "Recibimos varias consultas tuyas en la última hora. "
                     "Escribinos por WhatsApp y te respondemos al toque."
        }), 429

    nombre = _limpiar(datos.get("nombre") or datos.get("name"), MAX["nombre"])
    email = _limpiar(datos.get("email"), MAX["email"]).lower()
    area = _limpiar(datos.get("area"), MAX["area"])
    texto = _limpiar(datos.get("mensaje") or datos.get("message"), MAX["mensaje"])

    errores = {}
    if len(nombre) < MIN["nombre"]:
        errores["nombre"] = "Decinos cómo te llamás."
    if not RE_EMAIL.match(email):
        errores["email"] = "Revisá el email, parece que tiene un error."
    if len(texto) < MIN["mensaje"]:
        errores["mensaje"] = "Contanos un poco más para poder ayudarte."
    if errores:
        return jsonify({"ok": False, "errores": errores,
                        "error": "Revisá los datos marcados."}), 400

    if area not in AREAS:
        area = AREA_POR_DEFECTO

    mensaje = {
        "fecha": datetime.datetime.now().isoformat(timespec="seconds"),
        "nombre": nombre,
        "email": email,
        "area": area,
        "mensaje": texto,
        "ip": _ip(),
        "origen": _sin_saltos(_limpiar(request.headers.get("Referer"), 200)),
    }

    try:
        guardar(mensaje)
    except OSError as err:
        log.exception("No se pudo guardar el mensaje de contacto")
        return jsonify({
            "ok": False,
            "error": "No pudimos registrar tu consulta. Probá por WhatsApp, por favor."
        }), 500

    _registrar_envio()

    enviado, detalle = enviar_mail(mensaje)
    if not enviado:
        # El visitante no tiene la culpa: su mensaje está guardado.
        log.warning("Mensaje guardado pero no enviado por mail (%s)", detalle)

    return jsonify({
        "ok": True,
        "mensaje": "¡Gracias! Recibimos tu consulta y te vamos a contactar a la brevedad."
    })
