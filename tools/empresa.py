"""
Datos de la empresa — la base de todo lo demás.

Este módulo no importa nada del proyecto, así que lo pueden usar tanto
plantilla.py como servicios.py sin importarse entre sí.

Si cambia el teléfono, el dominio o el canal, se cambia SOLO acá y se corre:

    python3 tools/generar-servicios.py
    python3 tools/actualizar-nav.py
    python3 tools/generar-blog.py
"""

SITE = "https://www.surfinanzas.com.ar"

# --- WhatsApp de atención -------------------------------------------------
# Es el de todos los botones e íconos de WhatsApp del sitio.
WA_NUMERO = "5491164827010"             # para wa.me: sin +, ni espacios, ni guiones

_WA_TEXTO = "?text=Hola%20Sur%20Finanzas%2C%20quiero%20hacer%20una%20consulta."
WA = f"https://wa.me/{WA_NUMERO}{_WA_TEXTO}"

# --- Teléfono de la sucursal -----------------------------------------------
# Se muestra en los datos de la sucursal. En Contacto, el botón de la
# sucursal también lleva a este número.
TEL_DISPLAY = "+54 9 11 3396-1599"      # como se muestra en pantalla
TEL_E164 = "+5491133961599"             # para los enlaces tel:
WA_SUCURSAL = f"https://wa.me/{TEL_E164.lstrip('+')}{_WA_TEXTO}"

# --- Canal de WhatsApp -----------------------------------------------------
CANAL_URL = "https://whatsapp.com/channel/0029Vb8YV1u7YSdCLBxDnP3V"
CANAL_NOMBRE = "Sur Finanzas Central"
CANAL_TAGLINE = "El nuevo Surfi 🏄"
CANAL_SLOGAN = f"{CANAL_NOMBRE} · {CANAL_TAGLINE}"
CANAL_BAJADA = ("Novedades, cotizaciones y avisos, primero por el canal. "
                "Es de una sola vía: recibís todo sin que se te llene el chat.")

# --- Sucursal --------------------------------------------------------------
# La usa la página de oro, Nosotros y Contacto. Un solo lugar para los datos.
SUCURSAL = {
    "titulo": "Dónde encontrarnos",
    "bajada": "Plaza Canning, Buenos Aires.",
    "direccion": "Plaza Canning, locales 112 y 113 — Canning, Buenos Aires",
    "horario": "(a confirmar)",
    # El mapa se embebe por búsqueda de Google Maps: es interactivo y no
    # necesita API key. Con la dirección exacta o "lat,lng" el pin cae justo.
    "mapa_query": "Plaza Canning, Canning, Buenos Aires, Argentina",
    "mapa_link": "https://maps.app.goo.gl/o8fyNTN28JGUyiCj7",
}


def sucursal_datos():
    """Los datos en el formato (rótulo, valor[, enlace]) que espera el render."""
    return [
        ("Dirección", SUCURSAL["direccion"]),
        ("Teléfono", TEL_DISPLAY, "tel:" + TEL_E164),
        ("Horario", SUCURSAL["horario"]),
    ]


# --- Redes sociales --------------------------------------------------------
# Las URLs todavía no las tenemos: mientras estén en "" el enlace queda
# desactivado en vez de llevar a ninguna parte.
REDES = [
    {"clave": "instagram", "nombre": "Instagram", "usuario": "", "url": ""},
    {"clave": "tiktok",    "nombre": "TikTok",    "usuario": "", "url": ""},
    {"clave": "x",         "nombre": "X",         "usuario": "", "url": ""},
    {"clave": "youtube",   "nombre": "YouTube",   "usuario": "", "url": ""},
]
