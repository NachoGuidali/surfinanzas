#!/usr/bin/env python3
"""
Genera las páginas de servicios y la grilla del inicio a partir de
tools/servicios.py.

    python3 tools/generar-servicios.py

Escribe:
  - servicios/<archivo>.html    una página por servicio
  - index.html                  la grilla, entre los marcadores
                                <!-- servicios:inicio --> y <!-- servicios:fin -->

Los .html de servicios/ que ya no correspondan a ningún servicio se borran.
"""

import os
import re
import sys
import html
import json
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import servicios as S
import plantilla as T

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAIZ, "servicios")

MARCA_INI = "<!-- servicios:inicio -->"
MARCA_FIN = "<!-- servicios:fin -->"
CHIPS_INI = "<!-- servicios-chips:inicio -->"
CHIPS_FIN = "<!-- servicios-chips:fin -->"


def e(t):
    return html.escape(t or "", quote=True)


def wa(texto, numero=None):
    return f"https://wa.me/{numero or T.WA_NUMERO}?text=" + urllib.parse.quote(texto)


def badge(s):
    if not s.get("proximamente"):
        return ""
    return ' <span class="badge-proximamente">Próximamente</span>'


# ---------------------------------------------------------------------------
# Tarjeta del inicio
# ---------------------------------------------------------------------------

def tarjeta(s, i):
    clase = "service-card proximamente" if s.get("proximamente") else "service-card"

    # Con foto: la imagen del servicio. Sin foto: el ícono grande sobre el
    # degradé de marca — se ve intencional, no como un hueco.
    if s.get("imagen"):
        carga = "" if i < 2 else ' loading="lazy"'
        alt = s.get("imagen_alt") or ""
        thumb = (f'          <img src="{e(s["imagen"])}" alt="{e(alt)}" '
                 f'width="1280" height="720"{carga} />')
    else:
        thumb = (f'          <span class="service-thumb-icono" aria-hidden="true">'
                 f'{S.icono(s["icono"])}</span>')

    return f'''      <article class="{clase}" data-reveal>
        <div class="service-thumb">
{thumb}
        </div>
        <div class="service-card-body">
          <h3>{e(s["nombre"])}{badge(s)}</h3>
          <p><strong class="text-brand">{e(s["gancho"])}</strong> {e(s["resumen"])}</p>
          <div class="card-actions">
            <a href="servicios/{s["archivo"]}" class="btn btn-outline btn-sm">Conocé más &rarr;</a>
            <a href="{wa(s["wa"])}" class="btn btn-brand btn-sm" target="_blank" rel="noopener">{e(s["cta"])}</a>
          </div>
        </div>
      </article>'''


def grilla_inicio():
    tarjetas = "\n".join(tarjeta(s, i) for i, s in enumerate(S.SERVICIOS))
    return f'''{MARCA_INI}
    <div class="services-grid">

{tarjetas}

    </div>
    {MARCA_FIN}'''


ICONO_FOTO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<rect x="3" y="4" width="18" height="16" rx="2"/>'
              '<circle cx="8.5" cy="9.5" r="1.8"/>'
              '<path d="M21 15.5l-4.5-4.5L7 20"/></svg>')


def hero_figura(s):
    """La foto del encabezado, o el placeholder si todavía no la cargaron."""
    if s.get("imagen"):
        alt = s.get("imagen_alt") or ""
        return ('      <figure class="hero-figura" data-reveal="right">\n'
                f'        <img src="../{e(s["imagen"])}" alt="{e(alt)}" '
                'width="1200" height="900" />\n'
                '      </figure>')

    return ('      <figure class="hero-figura" data-reveal="right">\n'
            '        <div class="foto-placeholder">\n'
            f'          {ICONO_FOTO}\n'
            f'          <p class="fp-titulo">{e(s.get("foto_titulo") or ("Foto de " + S.corto(s)))}</p>\n'
            '        </div>\n'
            '      </figure>')

# ---------------------------------------------------------------------------
# Bloques extra (ej. custodia de mercadería dentro de transporte de caudales)
# ---------------------------------------------------------------------------

def pesos(n):
    """1500000 -> '$ 1.500.000' (formato argentino)."""
    return "$ " + f"{round(n):,}".replace(",", ".")


def figura(ctx, clase="bloque-figura"):
    """Foto del bloque, o placeholder si todavía no la cargaron."""
    if ctx.get("imagen"):
        alt = ctx.get("imagen_alt") or ""
        return (f'        <figure class="{clase}" data-reveal="scale">\n'
                f'          <img src="../{e(ctx["imagen"])}" alt="{e(alt)}" '
                'width="1200" height="900" loading="lazy" />\n'
                '        </figure>')
    return (f'        <figure class="{clase}" data-reveal="scale">\n'
            '          <div class="foto-placeholder">\n'
            f'            {ICONO_FOTO}\n'
            f'            <p class="fp-titulo">{e(ctx.get("foto_titulo", "Foto"))}</p>\n'
            '          </div>\n'
            '        </figure>')


CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="m5 12.5 4.5 4.5L19 7"/></svg>')


def bloques(s):
    salida = []
    for i, b in enumerate(s.get("bloques", [])):
        derecha = b.get("layout", "imagen-derecha") == "imagen-derecha"
        clase_sec = "section section-alt" if b.get("fondo") == "alt" else "section"

        cuerpo = []
        if b.get("eyebrow"):
            cuerpo.append(f'          <p class="eyebrow">{e(b["eyebrow"])}</p>')
        cuerpo.append(f'          <h2>{e(b["titulo"])}</h2>')
        if b.get("descripcion"):
            cuerpo.append(f'          <p class="muted mt-1">{e(b["descripcion"])}</p>')

        if b.get("items"):
            filas = "\n".join(
                '            <li>\n'
                f'              <span class="check-icono">{CHECK}</span>\n'
                f'              <span>{e(t)}</span>\n'
                '            </li>'
                for t in b["items"])
            cuerpo.append('          <ul class="lista-check mt-2">\n' + filas + '\n          </ul>')

        if b.get("para_quien"):
            cuerpo.append(
                '          <div class="para-quien mt-2">\n'
                '            <p class="eyebrow">Para qui&eacute;n</p>\n'
                f'            <p class="muted">{e(b["para_quien"])}</p>\n'
                '          </div>')

        if b.get("pasos"):
            filas = "\n".join(
                '            <li class="paso">\n'
                f'              <span class="paso-numero">{n + 1}</span>\n'
                '              <span class="paso-texto">\n'
                f'                <strong>{e(t)}</strong>\n'
                f'                <span class="muted">{e(d)}</span>\n'
                '              </span>\n'
                '            </li>'
                for n, (t, d) in enumerate(b["pasos"]))
            cuerpo.append(
                '          <p class="eyebrow mt-3">C&oacute;mo funciona</p>\n'
                '          <ol class="pasos">\n' + filas + '\n          </ol>')

        cuerpo.append(
            '          <div class="hero-actions start mt-3">\n'
            f'            <a href="{wa(b.get("wa", s["wa"]))}" class="btn btn-brand" '
            f'target="_blank" rel="noopener">{e(b.get("cta", s["cta"]))}</a>\n'
            '          </div>')

        texto = ('        <div class="bloque-texto" data-reveal="'
                 + ("left" if derecha else "right") + '">\n'
                 + "\n".join(cuerpo) + '\n        </div>')
        foto = figura(dict(b, foto_titulo=b.get("foto_titulo", f'Foto de {b["titulo"]}')))

        columnas = (texto, foto) if derecha else (foto, texto)

        salida.append(
            f'<section class="{clase_sec}">\n'
            '  <div class="container">\n'
            '    <div class="bloque-media">\n'
            + columnas[0] + '\n' + columnas[1] + '\n'
            '    </div>\n'
            '  </div>\n'
            '</section>')
    return "\n\n".join(salida)


# ---------------------------------------------------------------------------
# Para quién es · El proceso · Preguntas frecuentes
# Son opcionales: cada servicio las incluye si tiene los datos cargados.
# ---------------------------------------------------------------------------

def seccion_publico(s):
    p = s.get("publico")
    if not p:
        return ""
    cuerpo = ""
    if p.get("texto"):
        cuerpo = f'''
    <p class="lead max-46 mt-2" data-reveal>{e(p["texto"])}</p>'''
    if p.get("items"):
        tarjetas = "\n".join(
            f'''      <div class="card" data-reveal>
        <span class="check-icono">{CHECK}</span>
        <p class="mt-1">{e(t)}</p>
      </div>''' for t in p["items"])
        cuerpo += f'''
    <div class="grid grid-3 mt-4">
{tarjetas}
    </div>'''
    return f'''<section class="section">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">{e(p.get("eyebrow", "Para quién es"))}</p>
      <h2>{e(p["titulo"])}</h2>
      <p>{e(p["bajada"])}</p>
    </div>{cuerpo}
  </div>
</section>
'''


def seccion_proceso(s):
    p = s.get("proceso")
    if not p:
        return ""
    pasos = "\n".join(
        f'''      <li class="proceso-paso" data-reveal>
        <span class="proceso-numero">{i + 1}</span>
        <h3>{e(t)}</h3>
        <p class="muted">{e(d)}</p>
      </li>''' for i, (t, d) in enumerate(p["pasos"]))
    return f'''<section class="section section-alt">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">{e(p.get("eyebrow", "Cómo se hace"))}</p>
      <h2>{e(p["titulo"])}</h2>
      <p>{e(p["bajada"])}</p>
    </div>
    <ol class="proceso mt-4">
{pasos}
    </ol>
  </div>
</section>
'''


def seccion_faq(s):
    f = s.get("faq")
    if not f:
        return ""
    items = "\n".join(
        f'''      <details class="faq-item" data-reveal>
        <summary>
          <span>{e(p)}</span>
          <svg class="faq-flecha" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </summary>
        <div class="faq-respuesta"><p>{e(r)}</p></div>
      </details>''' for p, r in f["preguntas"])

    jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": p,
             "acceptedAnswer": {"@type": "Answer", "text": r}}
            for p, r in f["preguntas"]
        ],
    }

    return f'''<section class="section">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">Dudas frecuentes</p>
      <h2>{e(f["titulo"])}</h2>
      <p>{e(f["bajada"])}</p>
    </div>
    <div class="faq mt-4">
{items}
    </div>
  </div>
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</section>
'''

# ---------------------------------------------------------------------------
# Secciones libres: un título y una grilla de tarjetas.
# Sirven para "Qué cheques operamos", "El diferencial", etc.
# ---------------------------------------------------------------------------

def secciones(s):
    salida = []
    for sec in s.get("secciones", []):
        clase = "section section-alt" if sec.get("fondo") == "alt" else "section"

        bajada = f'\n      <p>{e(sec["bajada"])}</p>' if sec.get("bajada") else ""

        intro = ""
        if sec.get("texto"):
            intro = f'\n      <p>{e(sec["texto"])}</p>'

        tarjetas = ""
        if sec.get("tarjetas"):
            n = len(sec["tarjetas"])
            grid = "max-46" if n == 1 else ("grid-2" if n == 2 else ("grid-3" if n == 3 else "grid-4"))
            filas = "\n".join(
                f'''      <div class="card" data-reveal>
        <div class="icon-badge idle-float d{(i % 6) + 1}">{S.icono(s["icono"])}</div>
        <h3>{e(t)}</h3>
        <p class="muted mt-1">{e(d)}</p>
      </div>''' for i, (t, d) in enumerate(sec["tarjetas"]))
            tarjetas = f'\n    <div class="grid {grid} mt-4">\n{filas}\n    </div>'

        salida.append(f'''<section class="{clase}">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">{e(sec.get("eyebrow", sec["titulo"]))}</p>
      <h2>{e(sec["titulo"])}</h2>{bajada}{intro}
    </div>{tarjetas}
  </div>
</section>''')
    return "\n\n".join(salida)


# ---------------------------------------------------------------------------
# Mockup de la app y video
# ---------------------------------------------------------------------------

ICONO_PLAY = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<circle cx="12" cy="12" r="9.5"/><path d="M10 8.5l6 3.5-6 3.5z"/></svg>')


def seccion_app(s):
    a = s.get("app")
    if not a:
        return ""

    # Capturas que YA traen el marco del teléfono dibujado: se muestran tal
    # cual, sin envolverlas en otro marco.
    if a.get("imagenes"):
        pantallas = "\n".join(
            f'''      <figure class="captura-app" data-reveal="scale" style="--i:{i};">
        <img src="../{e(img["src"])}" alt="{e(img.get("alt", ""))}"
             width="{img.get("ancho", 360)}" height="{img.get("alto", 660)}" loading="lazy" />
      </figure>''' for i, img in enumerate(a["imagenes"]))
        visual = f'''    <div class="capturas-app mt-4">
{pantallas}
    </div>'''
    else:
        # Captura sin marco (o todavía sin cargar): va dentro del mockup.
        if a.get("imagen"):
            contenido = (f'<img src="../{e(a["imagen"])}" alt="{e(a.get("imagen_alt", ""))}" '
                         'width="390" height="844" />')
        else:
            contenido = (f'<div class="foto-placeholder">{ICONO_FOTO}'
                         f'<p class="fp-titulo">Mockup de {e(a["titulo"])}</p></div>')
        visual = f'''    <div class="mockup-telefono mt-4" data-reveal="scale">
      <div class="mockup-pantalla">{contenido}</div>
    </div>'''

    return f'''<section class="section section-alt">
  <div class="container">
    <div class="section-heading center" data-reveal>
      <p class="eyebrow">La app</p>
      <h2>{e(a["titulo"])}</h2>
      <p>{e(a["bajada"])}</p>
    </div>
{visual}
  </div>
</section>'''


def seccion_video(s):
    v = s.get("video")
    if not v:
        return ""
    if v.get("archivo"):
        contenido = (f'<video controls preload="metadata"'
                     + (f' poster="../{e(v["poster"])}"' if v.get("poster") else "")
                     + f'><source src="../{e(v["archivo"])}" type="video/mp4" /></video>')
    else:
        contenido = (f'<div class="foto-placeholder">{ICONO_PLAY}'
                     f'<p class="fp-titulo">{e(v.get("estado", "Video en producción"))}</p></div>')

    return f'''<section class="section">
  <div class="container">
    <div class="section-heading center" data-reveal>
      <p class="eyebrow">En video</p>
      <h2>{e(v["titulo"])}</h2>
      <p>{e(v["bajada"])}</p>
    </div>
    <figure class="marco-video mt-4" data-reveal="scale">{contenido}</figure>
  </div>
</section>'''

# ---------------------------------------------------------------------------
# Banner de atención personalizada por WhatsApp
# ---------------------------------------------------------------------------

def seccion_atencion(s):
    a = s.get("atencion")
    if not a:
        return ""
    enlace = wa(a.get("wa", s["wa"]), a.get("numero"))
    return f'''<section class="section">
  <div class="container">
    <div class="atencion-banda" data-reveal>
      <span class="atencion-icono" aria-hidden="true">{T.WA_ICON}</span>
      <div class="atencion-texto">
        <p class="eyebrow">{e(a.get("eyebrow", "Atención personalizada"))}</p>
        <h2>{e(a["titulo"])}</h2>
        <p class="muted">{e(a["bajada"])}</p>
      </div>
      <a href="{e(enlace)}" class="btn btn-canal" target="_blank" rel="noopener">
        {T.WA_ICON} {e(a.get("boton", "Escribinos por WhatsApp"))}
      </a>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------------------
# Dónde encontrarnos: datos de la sucursal + mapa interactivo
# ---------------------------------------------------------------------------

def seccion_ubicacion(s):
    """La sucursal. Los datos salen de empresa.py; acá solo se ajusta el CTA."""
    u = s.get("ubicacion")
    if not u:
        return ""
    return T.sucursal_block(
        eyebrow=u.get("eyebrow", "La sucursal"),
        cta=u.get("cta", s["cta"]),
        wa=wa(u.get("wa", s["wa"])),
    )


# ---------------------------------------------------------------------------
# Simulador de cuotas
# ---------------------------------------------------------------------------

def simulador(s):
    sim = S.config_simulador(s)
    if not sim:
        return ""

    # Valores de arranque, ya renderizados: la página no queda en blanco
    # si el JS todavía no corrió (o está bloqueado).
    tasa = sim["tasa_mensual"]
    n = sim["plazo_inicial"]
    capital = sim["inicial"]
    cuota_ini = capital * tasa / (1 - (1 + tasa) ** -n) if tasa > 0 else capital / n

    botones = "\n".join(
        f'            <button type="button" class="btn btn-sm plazo-btn '
        f'{"btn-brand" if p == sim["plazo_inicial"] else "btn-outline"}" '
        f'data-plazo="{p}" aria-pressed="{str(p == sim["plazo_inicial"]).lower()}">{p}</button>'
        for p in sim["plazos"])

    return (
        '<section class="section section-alt">\n'
        '  <div class="container">\n'
        '    <div class="section-heading center" data-reveal>\n'
        '      <p class="eyebrow">Simulador</p>\n'
        '      <h2>Calcul&aacute; tu cuota</h2>\n'
        '      <p>Un c&aacute;lculo orientativo, para que tengas una idea antes de escribirnos.</p>\n'
        '    </div>\n\n'
        '    <div class="card glass max-34 mt-4" data-reveal id="simulador"\n'
        f'         data-tasa="{sim["tasa_mensual"]}"\n'
        f'         data-wa="{wa(s["wa"])}"\n'
        '         style="margin-inline:auto;">\n\n'
        '      <div class="form-field">\n'
        '        <label for="sim-monto">Monto: <span id="sim-monto-label" class="valor-sim">'
        f'{pesos(capital)}</span></label>\n'
        f'        <input type="range" id="sim-monto" min="{sim["minimo"]}" max="{sim["maximo"]}" '
        f'step="{sim["paso"]}" value="{sim["inicial"]}" />\n'
        '        <div class="rango-limites">\n'
        f'          <span>{pesos(sim["minimo"])}</span><span>{pesos(sim["maximo"])}</span>\n'
        '        </div>\n'
        '      </div>\n\n'
        '      <div class="form-field">\n'
        '        <label id="lbl-plazo">Plazo (meses)</label>\n'
        '        <div id="sim-plazo" class="plazos" role="group" aria-labelledby="lbl-plazo">\n'
        f'{botones}\n'
        '        </div>\n'
        '      </div>\n\n'
        '      <div class="grid grid-2 sim-resultado">\n'
        '        <div>\n'
        '          <p class="muted chico">Cuota mensual</p>\n'
        f'          <p id="sim-cuota" class="stat-value">{pesos(cuota_ini)}</p>\n'
        '        </div>\n'
        '        <div>\n'
        '          <p class="muted chico">Total a pagar</p>\n'
        f'          <p id="sim-total" class="stat-value neutro">{pesos(cuota_ini * n)}</p>\n'
        '        </div>\n'
        '      </div>\n\n'
        '      <p class="sim-aclaracion">\n'
        '        <strong>Valores estimativos.</strong> No constituyen una oferta ni una aprobaci&oacute;n.\n'
        '        La propuesta final se define en la evaluaci&oacute;n con nuestro equipo comercial.\n'
        '      </p>\n\n'
        f'      <a id="sim-cta" href="{wa(s["wa"])}" class="btn btn-brand btn-block mt-2" '
        f'target="_blank" rel="noopener">{e(s["cta"])}</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>')


# ---------------------------------------------------------------------------
# Página de servicio
# ---------------------------------------------------------------------------

def puntos(s):
    filas = []
    for i, (titulo, detalle) in enumerate(s["puntos"]):
        filas.append(f'''      <div class="card" data-reveal>
        <div class="icon-badge idle-float d{(i % 6) + 1}">{S.icono(s["icono"])}</div>
        <h3>{e(titulo)}</h3>
        <p class="muted mt-1">{e(detalle)}</p>
      </div>''')
    return "\n".join(filas)


def otros_servicios(actual):
    enlaces = "\n".join(
        f'        <a href="{o["archivo"]}">{e(S.corto(o))}</a>'
        for o in S.SERVICIOS if o["archivo"] != actual["archivo"])
    return f'''<section class="section section-alt">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">Seguí explorando</p>
      <h2>Otros servicios de Sur Finanzas</h2>
    </div>
    <div class="service-nav" data-reveal>
{enlaces}
    </div>
  </div>
</section>'''


def seccion_puntos(s):
    """La grilla genérica de 'En detalle'. Se omite si el servicio no la usa."""
    if not s.get("puntos"):
        return ""
    grid = "grid grid-2" if len(s["puntos"]) <= 2 else "grid grid-4"
    return f'''<section class="section">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">En detalle</p>
      <h2>Cómo funciona</h2>
    </div>
    <div class="{grid} mt-4">
{puntos(s)}
    </div>
  </div>
</section>
'''


# Cada servicio puede definir su propio "orden". Si no lo hace, se usa este.
ORDEN_POR_DEFECTO = ["puntos", "publico", "proceso", "secciones",
                     "bloques", "app", "video", "simulador", "ubicacion", "faq"]

RENDERIZADORES = {
    "puntos": lambda s: seccion_puntos(s),
    "publico": lambda s: seccion_publico(s),
    "proceso": lambda s: seccion_proceso(s),
    "secciones": lambda s: secciones(s),
    "bloques": lambda s: bloques(s),
    "app": lambda s: seccion_app(s),
    "video": lambda s: seccion_video(s),
    "simulador": lambda s: simulador(s),
    "faq": lambda s: seccion_faq(s),
    "ubicacion": lambda s: seccion_ubicacion(s),
    "atencion": lambda s: seccion_atencion(s),
}


def cuerpo_secciones(s):
    """Arma el cuerpo de la página en el orden que pida el servicio."""
    orden = s.get("orden") or ORDEN_POR_DEFECTO
    desconocidas = [k for k in orden if k not in RENDERIZADORES]
    if desconocidas:
        raise SystemExit(
            f"✗ {s['archivo']}: sección desconocida en «orden»: {desconocidas}\n"
            f"  Válidas: {sorted(RENDERIZADORES)}")
    partes = [RENDERIZADORES[k](s) for k in orden]
    return "\n\n".join(p for p in partes if p.strip())


def render(s):
    titulo_seo = f"{s['nombre']} — Sur Finanzas"

    aviso = ""
    if s.get("proximamente"):
        aviso = '''
    <div class="aviso-proximamente" data-reveal>
      <p><strong>Este servicio todavía no está disponible.</strong>
      Estamos trabajando para lanzarlo. Escribinos y te avisamos apenas abra.</p>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(titulo_seo)}</title>
<meta name="description" content="{e(s["resumen"])}" />
{T.head_block("../", e(titulo_seo), e(s["resumen"]), f"servicios/{s['archivo']}")}
</head>
<body>
{T.header_block("../", "servicios")}

<section class="page-hero hero-split">
  <div class="bg-blob-wrap" aria-hidden="true">
    <div class="bg-blob" style="width:26rem; height:26rem; top:-8rem; right:-6rem;"></div>
    <div class="bg-blob b2" style="width:20rem; height:20rem; bottom:-10rem; left:-6rem;"></div>
  </div>
  <div class="container">
    <nav class="breadcrumb" aria-label="Migas de pan" data-reveal>
      <a href="../index.html">Inicio</a> <span>/</span>
      <a href="../index.html#servicios">Servicios</a> <span>/</span> {e(S.corto(s))}
    </nav>

    <div class="hero-split-grid">
      <div>
        <p class="eyebrow eyebrow-pill" data-reveal="left">{e(s["nombre"])}{badge(s)}</p>
        <h1 data-reveal="left" style="--reveal-delay:.08s;">{e(s["titulo"])}</h1>
        <p class="hero-bajada" data-reveal="left" style="--reveal-delay:.16s;">{e(s["descripcion"])}</p>
        <div class="hero-actions start mt-3" data-reveal="left" style="--reveal-delay:.24s;">
          <a href="{wa(s["wa"])}" class="btn btn-brand" target="_blank" rel="noopener">{e(s["cta"])}</a>
          <a href="../contacto.html" class="btn btn-outline">Otros canales</a>
        </div>{aviso}
      </div>

{hero_figura(s)}
    </div>
  </div>
</section>

{cuerpo_secciones(s)}
{otros_servicios(s)}

<section class="section">
  <div class="container">
    <div class="cta-frame">
      <video autoplay muted loop playsinline preload="metadata" poster="../assets/cta/hero2_1st-frame.png">
        <source src="../assets/cta/bg2-final.mp4" type="video/mp4" />
      </video>
      <div class="hero-overlay" aria-hidden="true"></div>
      <div class="cta-content" data-reveal>
        <h2>&iquest;Hablamos?</h2>
        <p>Contanos qu&eacute; necesit&aacute;s y te ayudamos a encontrar la mejor soluci&oacute;n.</p>
        <div class="cta-actions">
          <a href="{wa(s["wa"])}" class="btn btn-brand" target="_blank" rel="noopener">{e(s["cta"])}</a>
          <a href="../contacto.html" class="btn btn-outline">Otros canales</a>
        </div>
      </div>
    </div>
  </div>
</section>

{T.footer_block("../")}

{T.whatsapp_block()}

<script src="../js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------------------

NUMEROS = {1: "Un", 2: "Dos", 3: "Tres", 4: "Cuatro", 5: "Cinco", 6: "Seis",
           7: "Siete", 8: "Ocho", 9: "Nueve", 10: "Diez", 11: "Once", 12: "Doce"}


def revisar_numero_escrito():
    """Avisa si algún título dice un número de servicios que ya no es el real.

    El inicio y Nosotros tienen títulos del tipo "Cinco servicios, un mismo
    respaldo". Como no son generados, es fácil que queden desfasados al sumar
    o sacar un servicio.
    """
    correcto = NUMEROS.get(len(S.SERVICIOS), str(len(S.SERVICIOS)))
    patron = re.compile(r"\b(" + "|".join(NUMEROS.values()) + r")\s+servicios", re.I)
    avisos = []
    for rel in ("index.html", "nosotros.html"):
        ruta = os.path.join(RAIZ, rel)
        if not os.path.exists(ruta):
            continue
        for m in patron.finditer(open(ruta, encoding="utf-8").read()):
            if m.group(1).lower() != correcto.lower():
                avisos.append(f"{rel}: dice «{m.group(0)}» y hay {len(S.SERVICIOS)}")
    if avisos:
        print("\n  ⚠ Revisá estos títulos:")
        for a in avisos:
            print(f"    · {a}")


def main():
    os.makedirs(DIR, exist_ok=True)

    validos = {s["archivo"] for s in S.SERVICIOS}
    for f in os.listdir(DIR):
        if f.endswith(".html") and f not in validos:
            os.remove(os.path.join(DIR, f))
            print(f"  – borrada (ya no es un servicio): servicios/{f}")

    for s in S.SERVICIOS:
        destino = os.path.join(DIR, s["archivo"])
        open(destino, "w", encoding="utf-8").write(render(s))
        marca = "  (próximamente)" if s.get("proximamente") else ""
        print(f"  ✓ servicios/{s['archivo']}{marca}")

    # Grilla del inicio
    ruta_index = os.path.join(RAIZ, "index.html")
    idx = open(ruta_index, encoding="utf-8").read()
    patron = re.compile(re.escape(MARCA_INI) + r".*?" + re.escape(MARCA_FIN), re.S)
    if not patron.search(idx):
        raise SystemExit(
            f"✗ index.html no tiene los marcadores {MARCA_INI} … {MARCA_FIN}.\n"
            "  Agregalos alrededor de la grilla de servicios y volvé a correr esto.")
    idx = patron.sub(lambda _: grilla_inicio(), idx, count=1)
    open(ruta_index, "w", encoding="utf-8").write(idx)
    print(f"  ✓ index.html   (grilla con {len(S.SERVICIOS)} servicios)")

    # Chips de servicios en nosotros.html
    ruta_nos = os.path.join(RAIZ, "nosotros.html")
    nos = open(ruta_nos, encoding="utf-8").read()
    chips = "\n".join(
        f'      <a href="servicios/{x["archivo"]}">{e(S.corto(x))}</a>' for x in S.SERVICIOS)
    patron_chips = re.compile(re.escape(CHIPS_INI) + r".*?" + re.escape(CHIPS_FIN), re.S)
    if patron_chips.search(nos):
        nos = patron_chips.sub(lambda _: f"{CHIPS_INI}\n{chips}\n    {CHIPS_FIN}", nos, count=1)
        open(ruta_nos, "w", encoding="utf-8").write(nos)
        print("  ✓ nosotros.html   (chips de servicios)")

    revisar_numero_escrito()

    print("\nListo. Acordate de correr también:")
    print("  python3 tools/actualizar-nav.py")
    print("  python3 tools/generar-blog.py")


if __name__ == "__main__":
    main()
