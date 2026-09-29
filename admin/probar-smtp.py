#!/usr/bin/env python3
"""
Prueba el envío de correo con lo que hay cargado en admin/.env.

    .venv/bin/python admin/probar-smtp.py                 # solo conecta y autentica
    .venv/bin/python admin/probar-smtp.py Info@surfinanzas.com.ar   # además manda una prueba

Sirve para separar los dos problemas típicos: que no conecte (host, puerto,
cifrado) o que no autentique (usuario, contraseña, autenticación moderna).
No escribe nada ni toca la configuración.
"""

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def cargar_env():
    ruta = os.path.join(BASE, ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def main():
    cargar_env()

    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        print("✗ SMTP_HOST está vacío en admin/.env")
        return 1

    puerto = int(os.environ.get("SMTP_PUERTO", "587"))
    usuario = os.environ.get("SMTP_USUARIO", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "")
    desde = os.environ.get("SMTP_DESDE", "").strip() or usuario
    seguridad = os.environ.get("SMTP_SEGURIDAD", "starttls").strip().lower()

    print(f"Servidor:  {host}:{puerto} ({seguridad})")
    print(f"Usuario:   {usuario}")
    print(f"Remitente: {desde}")
    print(f"Contraseña: {'cargada' if password else '✗ VACÍA'}\n")

    contexto = ssl.create_default_context()
    try:
        if seguridad == "ssl":
            servidor = smtplib.SMTP_SSL(host, puerto, timeout=20, context=contexto)
        else:
            servidor = smtplib.SMTP(host, puerto, timeout=20)
        with servidor:
            print("✓ Conectado")
            if seguridad == "starttls":
                servidor.starttls(context=contexto)
                print("✓ STARTTLS")
            if usuario:
                servidor.login(usuario, password)
                print("✓ Autenticado")

            if len(sys.argv) > 1:
                destino = sys.argv[1]
                msg = EmailMessage()
                msg["Subject"] = "[Web] Prueba de envío"
                msg["From"] = desde
                msg["To"] = destino
                msg.set_content(
                    "Prueba de envío del formulario de surfinanzas.com.ar.\n"
                    "Si te llegó esto, el correo del formulario ya funciona.\n")
                servidor.send_message(msg)
                print(f"✓ Enviado a {destino}")
            else:
                print("\n(Para mandar una prueba: agregá una dirección al comando)")
    except smtplib.SMTPAuthenticationError as err:
        print(f"\n✗ No autenticó: {err}")
        print("  Suele ser: SMTP autenticado apagado en esa casilla, MFA sin"
              " excepción, o el inquilino ya no acepta autenticación básica.")
        return 1
    except Exception as err:
        print(f"\n✗ {type(err).__name__}: {err}")
        return 1

    print("\nListo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
