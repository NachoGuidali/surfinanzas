"""
Piezas compartidas del sitio (head, header, footer, botón de WhatsApp).

Todas las páginas se arman con estas funciones para que la navegación
sea idéntica en todos lados. Si tocás el menú, tocalo acá y después corré:

    python3 tools/actualizar-nav.py      # páginas fijas
    python3 tools/generar-blog.py        # blog

`prefix` es la ruta relativa hasta la raíz del sitio: "" para las páginas
de la raíz y "../" para las de servicios/ y blog/.
"""

import html as _html
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from empresa import (          # noqa: F401 — se reexportan a propósito
    SITE, TEL_DISPLAY, TEL_E164, WA_NUMERO, WA, WA_SUCURSAL,
    CANAL_URL, CANAL_NOMBRE, CANAL_TAGLINE, CANAL_SLOGAN, CANAL_BAJADA,
    SUCURSAL, sucursal_datos, REDES,
)

# Los servicios se definen en tools/servicios.py — no duplicar la lista acá.
import servicios as _servicios

SERVICES = _servicios.pares()

CARET = ('<svg class="nav-caret" width="12" height="12" viewBox="0 0 24 24" fill="none" '
         'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" '
         'aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>')

WA_ICON = ('<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16.01 3C9.38 3 4 8.38 4 '
           '15.01c0 2.5.73 4.83 2 6.78L4 29l7.4-1.94a11.9 11.9 0 0 0 4.6.94h.01c6.63 0 12.01-5.38 12.01-12.01C28.02 '
           '8.38 22.64 3 16.01 3Zm7.02 17.18c-.3.83-1.7 1.58-2.35 1.68-.6.09-1.36.13-2.19-.14-.5-.16-1.15-.37-1.98-.73'
           '-3.48-1.5-5.76-5.02-5.94-5.25-.17-.23-1.42-1.89-1.42-3.6 0-1.72.9-2.56 1.22-2.91.31-.35.68-.44.91-.44.23 0 '
           '.46 0 .66.01.21.01.5-.08.78.6.3.72 1.01 2.48 1.1 2.66.09.18.15.39.03.63-.12.24-.18.39-.36.6-.18.21-.38.47'
           '-.54.63-.18.18-.37.37-.16.72.21.35.94 1.55 2.02 2.51 1.39 1.24 2.56 1.62 2.92 1.8.36.18.57.15.78-.09.21-.24'
           '.9-1.05 1.14-1.41.24-.36.48-.3.8-.18.33.12 2.08.98 2.44 1.16.36.18.6.27.68.42.09.15.09.85-.21 1.68Z"/></svg>')

CANAL_ICONO = (
    '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16.01 3C9.38 3 4 8.38 4 '
    '15.01c0 2.5.73 4.83 2 6.78L4 29l7.4-1.94a11.9 11.9 0 0 0 4.6.94h.01c6.63 0 12.01-5.38 12.01-12.01C28.02 '
    '8.38 22.64 3 16.01 3Zm7.02 17.18c-.3.83-1.7 1.58-2.35 1.68-.6.09-1.36.13-2.19-.14-.5-.16-1.15-.37-1.98-.73'
    '-3.48-1.5-5.76-5.02-5.94-5.25-.17-.23-1.42-1.89-1.42-3.6 0-1.72.9-2.56 1.22-2.91.31-.35.68-.44.91-.44.23 0 '
    '.46 0 .66.01.21.01.5-.08.78.6.3.72 1.01 2.48 1.1 2.66.09.18.15.39.03.63-.12.24-.18.39-.36.6-.18.21-.38.47'
    '-.54.63-.18.18-.37.37-.16.72.21.35.94 1.55 2.02 2.51 1.39 1.24 2.56 1.62 2.92 1.8.36.18.57.15.78-.09.21-.24'
    '.9-1.05 1.14-1.41.24-.36.48-.3.8-.18.33.12 2.08.98 2.44 1.16.36.18.6.27.68.42.09.15.09.85-.21 1.68Z"/></svg>')


# Marcas de las redes, dibujadas a mano para no depender de una librería
# externa (el sitio no carga nada de terceros salvo la tipografía).
ICONOS_RED = {
    "instagram": (
        '<rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4"/>'
        '<circle cx="12" cy="12" r="4.3"/>'
        '<circle cx="17.3" cy="6.7" r="1.25" fill="currentColor" stroke="none"/>'),
    "tiktok": (
        '<path d="M13.6 3v11.1a2.9 2.9 0 1 1-2.4-2.85"/>'
        '<path d="M13.6 3.4a5 5 0 0 0 4.9 4.2"/>'),
    "x": (
        '<path d="M3.2 3.2h3.9l4.6 6.1 5.3-6.1h2.1l-6.4 7.4 6.9 9.2h-3.9l-4.9-6.5-5.6 6.5H3.1l7-8.1z"'
        ' fill="currentColor" stroke="none"/>'),
    "youtube": (
        '<rect x="2.3" y="5.4" width="19.4" height="13.2" rx="4"/>'
        '<path d="M10.3 9.3l5 2.7-5 2.7z" fill="currentColor" stroke="none"/>'),
}


def icono_red(clave):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS_RED[clave]}</svg>')


def redes_pie():
    """Los íconos de redes del pie. Salen de la misma lista que el banner."""
    filas = []
    for r in REDES:
        icono = icono_red(r["clave"])
        if r.get("url"):
            filas.append(
                f'          <a href="{_e(r["url"])}" target="_blank" rel="noopener" '
                f'aria-label="{_e(r["nombre"])} de Sur Finanzas">{icono}</a>')
        else:
            # Sin URL todavía: se muestra apagado en vez de enlazar a la nada.
            filas.append(
                f'          <span class="sin-enlace" title="{_e(r["nombre"])}" '
                f'aria-hidden="true">{icono}</span>')
    return "\n".join(filas)


def redes_banner(titulo="Seguinos en redes",
                 bajada="Novedades, cotizaciones y detrás de escena, todos los días."):
    """Banner con las redes sociales. Se usa en Contacto.

    Si una red todavía no tiene URL, se muestra igual pero como texto: un
    enlace a ninguna parte es peor que un ícono que todavía no lleva a nada.
    """
    filas = []
    for r in REDES:
        cuerpo = (f'      <span class="red-icono">{icono_red(r["clave"])}</span>\n'
                  f'      <span class="red-nombre">{_e(r["nombre"])}</span>')
        if r.get("url"):
            filas.append(
                f'    <a class="red red-{r["clave"]}" href="{_e(r["url"])}" '
                f'target="_blank" rel="noopener" aria-label="{_e(r["nombre"])} de Sur Finanzas">\n'
                f'{cuerpo}\n    </a>')
        else:
            filas.append(
                f'    <span class="red red-{r["clave"]} sin-enlace">\n{cuerpo}\n    </span>')

    return f'''<section class="section" id="redes">
  <div class="container">
    <div class="redes-banda" data-reveal>
      <div class="redes-texto">
        <p class="eyebrow">Redes</p>
        <h2>{_e(titulo)}</h2>
        <p class="muted mt-1">{_e(bajada)}</p>
      </div>
      <div class="redes-lista">
{chr(10).join(filas)}
      </div>
    </div>
  </div>
</section>'''


def canal_banda(p=""):
    """La franja destacada del canal. Se usa en el inicio."""
    return f'''<section class="section" id="canal">
  <div class="container">
    <div class="canal-banda" data-reveal>
      <div class="canal-texto">
        <p class="eyebrow">Canal de WhatsApp</p>
        <h2 class="canal-titulo">
          {CANAL_NOMBRE}<br />
          <span class="canal-tagline">{CANAL_TAGLINE}</span>
        </h2>
        <p class="muted mt-1">{CANAL_BAJADA}</p>
      </div>
      <div class="canal-accion">
        <a href="{CANAL_URL}" class="btn btn-canal" target="_blank" rel="noopener">
          {CANAL_ICONO} Seguí el canal
        </a>
        <p class="canal-nota">Gratis, y te podés salir cuando quieras.</p>
      </div>
    </div>
  </div>
</section>'''


def sucursal_block(eyebrow="La sucursal", cta="Hablanos", wa=None, fondo="alt"):
    """Sección "Dónde encontrarnos": datos de la sucursal + mapa interactivo.

    La usan la página de oro, Nosotros y Contacto. Todos los enlaces que
    contiene son absolutos, así que no hace falta prefijo de ruta.
    """
    import html as _html
    import urllib.parse as _up

    def e(t):
        return _html.escape(t or "", quote=True)

    def fila(d):
        titulo, valor = d[0], d[1]
        enlace = d[2] if len(d) > 2 else None
        cuerpo = f'<a href="{e(enlace)}">{e(valor)}</a>' if enlace else e(valor)
        return ('        <div class="dato">\n'
                f'          <p class="eyebrow">{e(titulo)}</p>\n'
                f'          <p class="muted">{cuerpo}</p>\n'
                '        </div>')

    datos = "\n".join(fila(d) for d in sucursal_datos())
    clase = "section section-alt" if fondo == "alt" else "section"
    consulta = _up.quote(SUCURSAL["mapa_query"])

    return f'''<section class="{clase}" id="donde-estamos">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">{e(eyebrow)}</p>
      <h2>{e(SUCURSAL["titulo"])}</h2>
      <p>{e(SUCURSAL["bajada"])}</p>
    </div>

    <div class="ubicacion mt-4">
      <div class="ubicacion-datos" data-reveal="left">
{datos}
        <div class="hero-actions start mt-3">
          <a href="{wa or WA}" class="btn btn-brand" target="_blank" rel="noopener">{e(cta)}</a>
          <a href="{SUCURSAL["mapa_link"]}" class="btn btn-outline" target="_blank" rel="noopener">Cómo llegar</a>
        </div>
      </div>
      <div class="mapa" data-reveal="scale">
        <iframe
          src="https://www.google.com/maps?q={consulta}&amp;hl=es&amp;z=16&amp;output=embed"
          title="Mapa de {e(SUCURSAL["mapa_query"])}"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          allowfullscreen></iframe>
      </div>
    </div>
  </div>
</section>'''

def canal_tarjeta():
    """Tarjeta del canal. Se usa en Contacto, al lado de la de WhatsApp."""
    return f'''      <div class="card card-canal" data-reveal>
        <div class="icon-badge icono-canal">{CANAL_ICONO}</div>
        <h2 class="canal-titulo" style="font-size:1.2rem;">
          {CANAL_NOMBRE}<br />
          <span class="canal-tagline">{CANAL_TAGLINE}</span>
        </h2>
        <p class="muted mt-1">{CANAL_BAJADA}</p>
        <a href="{CANAL_URL}" class="btn btn-canal mt-2" target="_blank" rel="noopener">Segu&iacute; el canal</a>
      </div>'''


def canal_pie():
    """Tira compacta del canal, dentro del pie de página."""
    return f'''      <a class="canal-tira" href="{CANAL_URL}" target="_blank" rel="noopener">
        <span class="canal-tira-icono">{CANAL_ICONO}</span>
        <span class="canal-tira-texto">
          <strong>{CANAL_NOMBRE} <span class="canal-tagline-inline">{CANAL_TAGLINE}</span></strong>
          <span>Seguí el canal de WhatsApp para no perderte nada.</span>
        </span>
        <span class="canal-tira-flecha" aria-hidden="true">&rarr;</span>
      </a>'''

def head_block(p, title, desc, canonical, og_type="website", image=None, extra=""):
    """Bloque común del <head>: favicons, redes sociales, fuentes, css."""
    img = image or f"{SITE}/assets/branding/og-image.jpg"
    return f'''<link rel="icon" href="{p}assets/branding/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/branding/favicon-32.png" />
<link rel="apple-touch-icon" href="{p}assets/branding/apple-touch-icon.png" />
<link rel="manifest" href="{p}site.webmanifest" />
<meta name="theme-color" content="#0b0b0f" />
<link rel="canonical" href="{SITE}/{canonical}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="Sur Finanzas" />
<meta property="og:locale" content="es_AR" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{SITE}/{canonical}" />
<meta property="og:image" content="{img}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{desc}" />
<meta name="twitter:image" content="{img}" />{extra}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet" />
<link rel="stylesheet" href="{p}css/styles.css" />
<script>document.documentElement.classList.add("js");</script>'''


def _e(t):
    """Escapa el texto: los nombres de servicio pueden traer & u otros signos."""
    return _html.escape(str(t or ""), quote=True)


def header_block(p, active):
    """active: 'inicio' | 'servicios' | 'blog' | 'nosotros' | 'contacto' | ''"""
    def cls(key):
        return ' class="is-active" aria-current="page"' if active == key else ""

    desk_services = "\n".join(
        f'            <a href="{p}{href}">{_e(label)}</a>' for href, label in SERVICES)
    mob_services = "\n".join(
        f'              <a href="{p}{href}">{_e(label)}</a>' for href, label in SERVICES)
    svc_active = ' class="is-active"' if active == "servicios" else ""

    return f'''<div class="scroll-progress" aria-hidden="true"></div>

<header class="navbar">
  <div class="container">
    <div class="nav-left">
      <a href="{p}index.html" class="nav-logo" aria-label="Sur Finanzas — Ir al inicio">
        <img src="{p}assets/branding/logo-sur.png" alt="Sur Finanzas" width="560" height="217" />
      </a>
      <nav class="nav-links" aria-label="Navegación principal">
        <a href="{p}index.html"{cls("inicio")}>Inicio</a>
        <div class="nav-dropdown">
          <button type="button" aria-haspopup="true"{svc_active}>Servicios {CARET}</button>
          <div class="nav-dropdown-panel">
{desk_services}
          </div>
        </div>
        <a href="{p}blog/index.html"{cls("blog")}>Blog</a>
        <a href="{p}nosotros.html"{cls("nosotros")}>Nosotros</a>
        <a href="{p}contacto.html"{cls("contacto")}>Contacto</a>
      </nav>
    </div>
    <div class="nav-cta">
      <a href="{WA}" class="btn btn-brand" target="_blank" rel="noopener">Hablanos</a>
    </div>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu">
      <span></span><span></span><span></span>
      <span class="sr-only">Abrir menú</span>
    </button>
  </div>
</header>

<div class="mobile-menu" id="mobile-menu">
  <div class="container">
    <nav aria-label="Navegación móvil">
      <a href="{p}index.html"{cls("inicio")}>Inicio</a>
      <button type="button" class="mobile-sub-toggle" aria-expanded="false">Servicios {CARET}</button>
      <div class="mobile-sub">
        <div>
{mob_services}
        </div>
      </div>
      <a href="{p}blog/index.html"{cls("blog")}>Blog</a>
      <a href="{p}nosotros.html"{cls("nosotros")}>Nosotros</a>
      <a href="{p}contacto.html"{cls("contacto")}>Contacto</a>
    </nav>
    <div class="mobile-cta">
      <a href="{WA}" class="btn btn-brand" data-close target="_blank" rel="noopener">Hablanos por WhatsApp</a>
    </div>
    <a class="mobile-canal" href="{CANAL_URL}" data-close target="_blank" rel="noopener">
      {CANAL_ICONO} <span>Seguí el canal · <strong>{CANAL_TAGLINE}</strong></span>
    </a>
    <p class="mobile-contact">
      ¿Preferís escribirnos? <a href="mailto:Info@surfinanzas.com.ar">Info@surfinanzas.com.ar</a>
    </p>
  </div>
</div>

<div class="nav-spacer" aria-hidden="true"></div>'''


def footer_block(p):
    svc = "\n".join(f'          <a href="{p}{href}">{_e(label)}</a>' for href, label in SERVICES)
    return f'''<footer class="footer">
  <div class="container">
{canal_pie()}
    <div class="footer-top">
      <div class="footer-logo">
        <a href="{p}index.html" aria-label="Sur Finanzas — Ir al inicio">
          <img src="{p}assets/branding/logo-sur.png" alt="Sur Finanzas" width="560" height="217" />
        </a>
        <p class="muted">Oro, cheques, microcréditos, medios de pago, caudales y cajas. Un mismo respaldo para cada operación.</p>
        <div class="footer-social">
{redes_pie()}
        </div>
      </div>
      <div class="footer-cols">
        <div class="footer-col">
          <h4>Servicios</h4>
{svc}
        </div>
        <div class="footer-col">
          <h4>Empresa</h4>
          <a href="{p}nosotros.html">Nosotros</a>
          <a href="{p}blog/index.html">Blog</a>
          <a href="{p}contacto.html">Contacto</a>
          <a href="{WA}" target="_blank" rel="noopener">WhatsApp</a>
          <a href="{CANAL_URL}" target="_blank" rel="noopener">Canal de WhatsApp</a>
        </div>
        <div class="footer-col">
          <h4>Legales</h4>
          <a href="#">Términos y condiciones</a>
          <a href="#">Política de privacidad</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 2026 Sur Finanzas Group S.A. · CUIT 30-71740402-1</p>
      <p class="footer-legal">Proveedor de crédito no financiero habilitado por el BCRA, registro número 55.380. Domicilio legal: Seguí 776, Adrogué, Buenos Aires.</p>
    </div>
  </div>
</footer>'''


def whatsapp_block():
    return f'''<a href="{WA}" class="whatsapp-float" target="_blank" rel="noopener" aria-label="Hablar por WhatsApp">
  <span class="whatsapp-float-ring" aria-hidden="true"></span>
  <span class="whatsapp-float-ring delay" aria-hidden="true"></span>
  {WA_ICON}
</a>'''
