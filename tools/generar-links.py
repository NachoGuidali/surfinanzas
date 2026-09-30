#!/usr/bin/env python3
"""
Genera links.html: la landing tipo "link in bio" para el QR.

    python3 tools/generar-links.py

Es una página suelta, sin menú ni pie, con su propio CSS adentro: no depende
de css/styles.css. Los datos salen de tools/empresa.py, así que el WhatsApp y
las redes se mantienen solos.

Se ve en surfinanzas.com.ar/links (nginx resuelve /links -> links.html).
"""

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import empresa as E
import plantilla as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = "links.html"

TITULO = "Sur Finanzas — Links"
DESCRIPCION = ("Todos los links de Sur Finanzas en un solo lugar: Instagram, "
               "WhatsApp y reseñas de Google.")

RESENA = ("https://search.google.com/local/writereview"
          "?placeid=ChIJjSzQPqDXvJURyADOtLJa8Z8")

ICONO_ESTRELLA = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="m12 2.6 2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3.1-5.8 3.1 1.1-6.5'
    '-4.7-4.6 6.5-.9z"/></svg>')

ICONO_FLECHA = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def e(t):
    return html.escape(t or "", quote=True)


def red(clave):
    """Devuelve la red de empresa.py, o None si no está cargada."""
    return next((r for r in E.REDES if r["clave"] == clave and r.get("url")), None)


def boton(url, icono, titulo, detalle, clase=""):
    return f'''      <a class="enlace {clase}" href="{e(url)}" target="_blank" rel="noopener">
        <span class="enlace-icono" aria-hidden="true">{icono}</span>
        <span class="enlace-texto">
          <strong>{e(titulo)}</strong>
          <span>{e(detalle)}</span>
        </span>
        <span class="enlace-flecha" aria-hidden="true">{ICONO_FLECHA}</span>
      </a>'''


def enlaces():
    filas = []
    ig = red("instagram")
    if ig:
        filas.append(boton(ig["url"], T.icono_red("instagram"),
                           "Instagram", ig["usuario"] or "@surfinanzasok", "es-instagram"))

    filas.append(boton(E.WA, T.WA_ICON, "WhatsApp",
                       f"Escribinos al {E.WA_DISPLAY}", "es-whatsapp"))

    filas.append(boton(RESENA, ICONO_ESTRELLA, "Dejanos tu reseña",
                       "Contanos cómo te atendimos en Google", "es-resena"))
    return "\n".join(filas)


PAGINA = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(TITULO)}</title>
<meta name="description" content="{e(DESCRIPCION)}" />
<link rel="icon" href="assets/branding/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="assets/branding/favicon-32.png" />
<link rel="apple-touch-icon" href="assets/branding/apple-touch-icon.png" />
<meta name="theme-color" content="#0b0b0f" />
<link rel="canonical" href="{E.SITE}/links" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Sur Finanzas" />
<meta property="og:locale" content="es_AR" />
<meta property="og:title" content="{e(TITULO)}" />
<meta property="og:description" content="{e(DESCRIPCION)}" />
<meta property="og:url" content="{E.SITE}/links" />
<meta property="og:image" content="{E.SITE}/assets/branding/og-image.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet" />

<style>
  :root {{
    --fondo: #0b0b0f;
    --texto: #f5f6f8;
    --tenue: #9aa3b2;
    --marca: #09FED5;
    --borde: rgba(255, 255, 255, 0.1);
    --wa: #25d366;
  }}

  * {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    min-height: 100svh;
    background: var(--fondo);
    color: var(--texto);
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    display: grid;
    place-items: center;
    padding: 2.5rem 1.25rem 3rem;
  }}

  /* Fondo: el isotipo fijo, muy tenue, y dos manchas turquesas */
  body::before {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: -2;
    background: url("assets/branding/isotipo-sur.png") no-repeat center 45% / min(78vw, 26rem);
    opacity: 0.05;
    pointer-events: none;
  }}
  .manchas {{ position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }}
  .mancha {{
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    background: var(--marca);
  }}
  .m1 {{ width: 26rem; height: 26rem; top: -10rem; right: -8rem; opacity: 0.2; }}
  .m2 {{ width: 20rem; height: 20rem; bottom: -9rem; left: -7rem; opacity: 0.12; }}

  main {{ width: min(30rem, 100%); text-align: center; }}

  .logo {{ width: min(15rem, 62vw); height: auto; margin: 0 auto 1.5rem; display: block; }}

  /* "El nuevo Surfi", igual que en el inicio del sitio */
  .surfi-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0 0 1.75rem;
    padding: 0.5rem 1.2rem 0.5rem 1.05rem;
    border: 1px solid rgba(9, 254, 213, 0.32);
    border-radius: 999px;
    background: rgba(9, 254, 213, 0.1);
    color: var(--marca);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    box-shadow: 0 0 28px rgba(9, 254, 213, 0.16);
  }}
  .surfi {{
    display: inline-block;
    font-size: 1.7em;
    line-height: 1;
    letter-spacing: 0;
    transform-origin: 50% 80%;
    filter: drop-shadow(0 0 10px rgba(9, 254, 213, 0.45));
    animation: surfeando 2.8s ease-in-out infinite;
  }}
  @keyframes surfeando {{
    0%, 100% {{ transform: translateY(0) rotate(-8deg); }}
    20%  {{ transform: translateY(-5px) rotate(4deg); }}
    45%  {{ transform: translateY(2px) rotate(9deg); }}
    70%  {{ transform: translateY(-3px) rotate(-2deg); }}
    85%  {{ transform: translateY(1px) rotate(-6deg); }}
  }}

  .enlaces {{ display: grid; gap: 0.85rem; }}

  .enlace {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.15rem;
    border: 1px solid var(--borde);
    border-radius: 1.1rem;
    background: rgba(255, 255, 255, 0.035);
    color: inherit;
    text-decoration: none;
    text-align: left;
    transition: transform 0.25s ease, border-color 0.25s ease, background 0.25s ease;
  }}
  .enlace:hover, .enlace:focus-visible {{
    transform: translateY(-2px);
    border-color: rgba(9, 254, 213, 0.5);
    background: rgba(9, 254, 213, 0.07);
  }}
  .enlace:focus-visible {{ outline: 2px solid var(--marca); outline-offset: 3px; }}

  .enlace-icono {{
    display: grid;
    place-items: center;
    width: 2.9rem;
    height: 2.9rem;
    border-radius: 0.9rem;
    border: 1px solid var(--borde);
    background: rgba(255, 255, 255, 0.04);
    color: var(--marca);
  }}
  .enlace-icono svg {{ width: 1.45rem; height: 1.45rem; }}

  .enlace-texto {{ display: flex; flex-direction: column; min-width: 0; }}
  .enlace-texto strong {{ font-size: 1.02rem; font-weight: 600; }}
  .enlace-texto span {{ font-size: 0.86rem; color: var(--tenue); }}

  .enlace-flecha {{ color: var(--tenue); display: grid; place-items: center; }}
  .enlace-flecha svg {{ width: 1.1rem; height: 1.1rem; }}
  .enlace:hover .enlace-flecha {{ color: var(--marca); transform: translateX(3px); }}

  /* Cada botón con el color de su marca al pasar el mouse */
  .es-instagram:hover .enlace-icono {{ border-color: #E1306C; background: rgba(225, 48, 108, 0.14); color: #FF6E9C; }}
  .es-whatsapp .enlace-icono {{ color: var(--wa); }}
  .es-whatsapp:hover .enlace-icono {{ border-color: var(--wa); background: rgba(37, 211, 102, 0.14); }}
  .es-resena .enlace-icono {{ color: #FFC33D; }}
  .es-resena:hover .enlace-icono {{ border-color: #FFC33D; background: rgba(255, 195, 61, 0.14); }}

  .pie {{ margin-top: 2rem; font-size: 0.85rem; color: var(--tenue); }}
  .pie a {{ color: var(--marca); text-decoration: none; }}
  .pie a:hover {{ text-decoration: underline; }}

  @media (prefers-reduced-motion: reduce) {{
    .surfi {{ animation: none; }}
    .enlace, .enlace:hover {{ transform: none; }}
  }}
</style>
</head>
<body>

<div class="manchas" aria-hidden="true">
  <div class="mancha m1"></div>
  <div class="mancha m2"></div>
</div>

<main>
  <img class="logo" src="assets/branding/logo-sur.svg" alt="Sur Finanzas" width="399" height="155" />

  <p class="surfi-pill">{E.CANAL_TAGLINE.replace("🏄", '<span class="surfi" role="img" aria-label="surfista">🏄</span>')}</p>

  <div class="enlaces">
{enlaces()}
  </div>

  <p class="pie">
    <a href="{E.SITE}">surfinanzas.com.ar</a> · {e(E.SUCURSAL["bajada"].rstrip("."))}
  </p>
</main>

</body>
</html>
'''


if __name__ == "__main__":
    with open(os.path.join(ROOT, ARCHIVO), "w", encoding="utf-8") as fh:
        fh.write(PAGINA)
    print(f"  ✓ {ARCHIVO}")
