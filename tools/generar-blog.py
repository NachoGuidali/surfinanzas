#!/usr/bin/env python3
"""
Generador del blog de Sur Finanzas.

Lee los artículos en Markdown de blog/_posts/ y escribe:
  - blog/<slug>.html         una página por artículo
  - blog/index.html          el listado con buscador y filtros
  - sitemap.xml              actualizado con todas las URLs

Uso:
    python3 tools/generar-blog.py

Requiere:  pip install markdown

Cada .md arranca con un encabezado entre líneas de tres guiones:

    ---
    titulo: Cómo funciona el descuento de cheques
    resumen: Una frase que se muestra en la tarjeta del listado.
    fecha: 2026-08-10
    categoria: Cheques
    autor: Equipo Sur Finanzas
    imagen:                      # opcional, ej: assets/blog/cheques.jpg
    destacado: true              # opcional, lo pone arriba de todo
    borrador: false              # true = no se publica
    ---

    Acá va el cuerpo del artículo en Markdown.
"""

import os
import re
import sys
import html
import json
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantilla as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "blog", "_posts")
BLOG_DIR = os.path.join(ROOT, "blog")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

PAGINAS_FIJAS = [
    ("index.html", "1.0"), ("nosotros.html", "0.8"), ("contacto.html", "0.8"),
    ("blog/index.html", "0.9"),
] + [(h, "0.8") for h, _ in T.SERVICES]


# --------------------------------------------------------------------------
# Lectura de los .md
# --------------------------------------------------------------------------

def parsear_encabezado(texto):
    """Lee las líneas `clave: valor` del encabezado.

    Los valores pueden ir entre comillas dobles, y en ese caso se respeta
    todo lo que haya adentro (dos puntos, almohadillas, comillas escapadas
    con \\"). Sin comillas, un ` #` inicia un comentario.
    """
    meta = {}
    for linea in texto.splitlines():
        if not linea.strip() or linea.lstrip().startswith("#") or ":" not in linea:
            continue
        clave, valor = linea.split(":", 1)
        valor = valor.strip()
        if valor.startswith('"'):
            m = re.match(r'"((?:[^"\\]|\\.)*)"', valor)
            valor = m.group(1).replace('\\"', '"').replace("\\\\", "\\") if m else valor.strip('"')
        else:
            valor = re.split(r"\s+#", valor, maxsplit=1)[0].strip().strip("'")
        meta[clave.strip().lower()] = valor
    return meta


def leer_post(path):
    raw = open(path, encoding="utf-8").read().lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"✗ {os.path.basename(path)}: falta el encabezado entre --- y ---")

    meta = parsear_encabezado(m.group(1))

    cuerpo = m.group(2).strip()

    for req in ("titulo", "fecha"):
        if not meta.get(req):
            raise SystemExit(f"✗ {os.path.basename(path)}: falta '{req}' en el encabezado")

    try:
        fecha = datetime.date.fromisoformat(meta["fecha"])
    except ValueError:
        raise SystemExit(f"✗ {os.path.basename(path)}: fecha inválida '{meta['fecha']}' (usá AAAA-MM-DD)")

    nombre = os.path.basename(path)[:-3]
    slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", nombre)

    palabras = len(re.findall(r"\w+", cuerpo))

    return {
        "slug": slug,
        "titulo": meta["titulo"],
        "resumen": meta.get("resumen", ""),
        "fecha": fecha,
        "categoria": meta.get("categoria", "Notas"),
        "autor": meta.get("autor", "Equipo Sur Finanzas"),
        "imagen": meta.get("imagen", ""),
        "destacado": meta.get("destacado", "").lower() in ("true", "sí", "si", "1"),
        "borrador": meta.get("borrador", "").lower() in ("true", "sí", "si", "1"),
        "cuerpo": cuerpo,
        "minutos": max(1, round(palabras / 200)),
        "origen": os.path.basename(path),
    }


def a_html(md_text):
    try:
        import markdown
    except ImportError:
        raise SystemExit("✗ Falta la librería markdown.  Instalala con:  pip install markdown")
    return markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "smarty", "toc"],
        output_format="html5",
    )


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def e(s):
    return html.escape(s or "", quote=True)


# --------------------------------------------------------------------------
# Fragmentos reutilizables
# --------------------------------------------------------------------------

def thumb(post, prefix="", clase="post-thumb"):
    """Miniatura: imagen propia si hay, si no un degradé de marca con el isotipo."""
    if post["imagen"]:
        return (f'<div class="{clase}">'
                f'<img src="{prefix}{e(post["imagen"])}" alt="" loading="lazy" '
                f'width="1280" height="720" /></div>')
    return (f'<div class="{clase}">'
            f'<div class="post-thumb-mark" aria-hidden="true">'
            f'<img src="{prefix}assets/branding/isotipo-sur.png" alt="" loading="lazy" '
            f'width="256" height="256" /></div></div>')


def meta_linea(post):
    return (f'<div class="post-meta">'
            f'<time datetime="{post["fecha"].isoformat()}">{fecha_larga(post["fecha"])}</time>'
            f'<span class="sep">·</span><span>{post["minutos"]} min de lectura</span>'
            f'<span class="sep">·</span><span>{e(post["autor"])}</span>'
            f'</div>')


def tarjeta(post, destacada=False, href_prefijo="", img_prefijo="../"):
    """Tarjeta de nota. Los prefijos cambian según desde dónde se la use:
    dentro de blog/ los links son relativos; desde el inicio llevan blog/."""
    clase = "post-card featured" if destacada else "post-card"
    return f'''      <a class="{clase}" href="{href_prefijo}{post["slug"]}.html" data-categoria="{e(post["categoria"])}" data-reveal>
        {thumb(post, img_prefijo)}
        <div class="post-card-body">
          <span class="post-tag">{e(post["categoria"])}</span>
          <h3>{e(post["titulo"])}</h3>
          <p>{e(post["resumen"])}</p>
          {meta_linea(post)}
        </div>
      </a>'''


MARCA_HOME_INI = "<!-- blog-home:inicio -->"
MARCA_HOME_FIN = "<!-- blog-home:fin -->"


def seccion_home(posts, cantidad=3):
    """Las últimas notas, para mostrar en el inicio.

    Devuelve "" si no hay ninguna: mejor que quede sin sección a que quede
    un título con la grilla vacía.
    """
    ultimas = posts[:cantidad]
    if not ultimas:
        return ""

    # Desde el inicio los links van a blog/ y las imágenes salen de la raíz.
    tarjetas = "\n".join(
        tarjeta(p, href_prefijo="blog/", img_prefijo="") for p in ultimas)

    return f'''<section class="section" id="novedades">
  <div class="container">
    <div class="encabezado-novedades">
      <div class="section-heading" data-reveal>
        <p class="eyebrow">Del blog</p>
        <h2>Enterate de las &uacute;ltimas novedades</h2>
      </div>
      <a class="enlace-todas" href="blog/index.html" data-reveal>
        Ver todas las notas <span aria-hidden="true">&rarr;</span>
      </a>
    </div>
    <div class="post-grid">
{tarjetas}
    </div>
  </div>
</section>'''


def escribir_home(posts):
    """Inserta las últimas notas en index.html, entre los marcadores."""
    ruta = os.path.join(ROOT, "index.html")
    if not os.path.exists(ruta):
        return
    texto = open(ruta, encoding="utf-8").read()
    patron = re.compile(re.escape(MARCA_HOME_INI) + r".*?" + re.escape(MARCA_HOME_FIN), re.S)
    if not patron.search(texto):
        print(f"  ⚠ index.html no tiene los marcadores {MARCA_HOME_INI} … {MARCA_HOME_FIN}")
        return
    contenido = seccion_home(posts)
    texto = patron.sub(
        lambda _: f"{MARCA_HOME_INI}\n{contenido}\n{MARCA_HOME_FIN}", texto, count=1)
    open(ruta, "w", encoding="utf-8").write(texto)
    n = min(len(posts), 3)
    print(f"  ✓ index.html   (últimas {n} nota{'s' if n != 1 else ''})")

# --------------------------------------------------------------------------
# Página de artículo
# --------------------------------------------------------------------------

def render_post(post, anterior, siguiente, relacionados):
    url = f"{T.SITE}/blog/{post['slug']}.html"
    titulo_seo = f"{post['titulo']} — Blog de Sur Finanzas"
    imagen = f"{T.SITE}/{post['imagen']}" if post["imagen"] else None

    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["titulo"],
        "description": post["resumen"],
        "datePublished": post["fecha"].isoformat(),
        "author": {"@type": "Organization", "name": post["autor"]},
        "publisher": {
            "@type": "Organization",
            "name": "Sur Finanzas",
            "logo": {"@type": "ImageObject", "url": f"{T.SITE}/assets/branding/logo-sur.png"},
        },
        "mainEntityOfPage": url,
        "image": imagen or f"{T.SITE}/assets/branding/og-image.jpg",
        "inLanguage": "es-AR",
    }
    extra = ('\n<meta property="article:published_time" content="'
             + post["fecha"].isoformat() + '" />'
             '\n<meta property="article:section" content="' + e(post["categoria"]) + '" />'
             '\n<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + '</script>')

    texto_compartir = f"{post['titulo']} — Sur Finanzas"
    import urllib.parse as up
    q_txt, q_url = up.quote(texto_compartir), up.quote(url)

    share = f'''      <div class="post-share">
        <span>Compartir</span>
        <a href="https://wa.me/?text={q_txt}%20{q_url}" target="_blank" rel="noopener" aria-label="Compartir por WhatsApp">
          <svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16.01 3C9.38 3 4 8.38 4 15.01c0 2.5.73 4.83 2 6.78L4 29l7.4-1.94a11.9 11.9 0 0 0 4.6.94h.01c6.63 0 12.01-5.38 12.01-12.01C28.02 8.38 22.64 3 16.01 3Zm7.02 17.18c-.3.83-1.7 1.58-2.35 1.68-.6.09-1.36.13-2.19-.14-.5-.16-1.15-.37-1.98-.73-3.48-1.5-5.76-5.02-5.94-5.25-.17-.23-1.42-1.89-1.42-3.6 0-1.72.9-2.56 1.22-2.91.31-.35.68-.44.91-.44.23 0 .46 0 .66.01.21.01.5-.08.78.6.3.72 1.01 2.48 1.1 2.66.09.18.15.39.03.63-.12.24-.18.39-.36.6-.18.21-.38.47-.54.63-.18.18-.37.37-.16.72.21.35.94 1.55 2.02 2.51 1.39 1.24 2.56 1.62 2.92 1.8.36.18.57.15.78-.09.21-.24.9-1.05 1.14-1.41.24-.36.48-.3.8-.18.33.12 2.08.98 2.44 1.16.36.18.6.27.68.42.09.15.09.85-.21 1.68Z"/></svg>
        </a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={q_url}" target="_blank" rel="noopener" aria-label="Compartir en LinkedIn">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-.95 1.83-1.95 3.76-1.95C21.4 8.75 22 11 22 14.1V21h-4v-6.1c0-1.45-.03-3.3-2.05-3.3-2.06 0-2.37 1.57-2.37 3.2V21h-4z"/></svg>
        </a>
        <a href="https://twitter.com/intent/tweet?text={q_txt}&amp;url={q_url}" target="_blank" rel="noopener" aria-label="Compartir en X">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.65l-5.22-6.82-5.97 6.82H1.66l7.73-8.84L1.25 2.25h6.82l4.71 6.23zm-1.16 17.52h1.83L7.02 4.13H5.05z"/></svg>
        </a>
        <button type="button" data-copiar-link aria-label="Copiar el link del artículo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1.2 1.1"/><path d="M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1.2-1.1"/></svg>
        </button>
        <span class="copy-ok" role="status" aria-live="polite">¡Link copiado!</span>
      </div>'''

    pager = ""
    if anterior or siguiente:
        izq = (f'''        <a href="{anterior["slug"]}.html">
          <small>Artículo anterior</small>
          <strong>{e(anterior["titulo"])}</strong>
        </a>''' if anterior else "        <span></span>")
        der = (f'''        <a href="{siguiente["slug"]}.html" class="next">
          <small>Artículo siguiente</small>
          <strong>{e(siguiente["titulo"])}</strong>
        </a>''' if siguiente else "        <span></span>")
        pager = f'''      <nav class="post-pager" aria-label="Más artículos">
{izq}
{der}
      </nav>'''

    rel = ""
    if relacionados:
        cards = "\n".join(tarjeta(r) for r in relacionados)
        rel = f'''
<section class="section section-alt">
  <div class="container">
    <div class="section-heading" data-reveal>
      <p class="eyebrow">Seguí leyendo</p>
      <h2>Otras notas del blog</h2>
    </div>
    <div class="post-grid">
{cards}
    </div>
  </div>
</section>
'''

    if post["imagen"]:
        portada = f'<img src="../{e(post["imagen"])}" alt="" width="1600" height="686" />'
    else:
        portada = ('<div class="post-thumb-mark" aria-hidden="true">'
                   '<img src="../assets/branding/isotipo-sur.png" alt="" width="256" height="256" /></div>')
    cover = f'      <figure class="post-cover" data-reveal>{portada}</figure>'

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(titulo_seo)}</title>
<meta name="description" content="{e(post["resumen"])}" />
{T.head_block("../", e(titulo_seo), e(post["resumen"]), f"blog/{post['slug']}.html", og_type="article", image=imagen, extra=extra)}
</head>
<body>
{T.header_block("../", "blog")}

<article class="page-hero post-hero">
  <div class="bg-blob-wrap" aria-hidden="true">
    <div class="bg-blob" style="width:26rem; height:26rem; top:-8rem; right:-6rem;"></div>
    <div class="bg-blob b2" style="width:20rem; height:20rem; bottom:-10rem; left:-6rem;"></div>
  </div>
  <div class="container" style="position:relative; z-index:1;">
    <div class="post-layout">
      <nav class="breadcrumb" aria-label="Migas de pan" data-reveal>
        <a href="../index.html">Inicio</a> <span>/</span> <a href="index.html">Blog</a> <span>/</span> {e(post["categoria"])}
      </nav>
      <span class="post-tag" data-reveal>{e(post["categoria"])}</span>
      <h1 class="mt-1" data-reveal style="--reveal-delay:.1s;">{e(post["titulo"])}</h1>
      {meta_linea(post).replace('<div class="post-meta">', '<div class="post-meta" data-reveal style="--reveal-delay:.2s;">')}
    </div>
  </div>
</article>

<section class="section" style="padding-top:2rem;">
  <div class="container">
    <div class="post-layout">
{cover}
      <div class="prose mt-4" data-reveal>
{a_html(post["cuerpo"])}
      </div>
{share}
{pager}
    </div>
  </div>
</section>
{rel}
<section class="section">
  <div class="container">
    <div class="cta-frame">
      <video autoplay muted loop playsinline preload="metadata" poster="../assets/cta/hero2_1st-frame.png">
        <source src="../assets/cta/bg2-final.mp4" type="video/mp4" />
      </video>
      <div class="hero-overlay" aria-hidden="true"></div>
      <div class="cta-content" data-reveal>
        <h2>&iquest;Tenés una consulta?</h2>
        <p>Contanos qué necesitás y te ayudamos a encontrar la mejor solución.</p>
        <div class="cta-actions">
          <a href="{T.WA}" class="btn btn-brand" target="_blank" rel="noopener">Hablanos</a>
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


# --------------------------------------------------------------------------
# Página de listado
# --------------------------------------------------------------------------

def render_index(posts):
    titulo = "Blog — Sur Finanzas"
    desc = ("Notas sobre microcréditos, cheques, caudales, oro y cajas de seguridad. "
            "Educación financiera para comercios y emprendedores.")

    destacado = next((p for p in posts if p["destacado"]), posts[0] if posts else None)
    resto = [p for p in posts if p is not destacado]

    categorias = []
    for p in posts:
        if p["categoria"] not in categorias:
            categorias.append(p["categoria"])

    chips = [
        '        <button type="button" class="tag" data-filtro="todos" aria-pressed="true">'
        f'Todos <span class="tag-count">{len(posts)}</span></button>'
    ]
    for c in sorted(categorias):
        n = sum(1 for p in posts if p["categoria"] == c)
        chips.append(f'        <button type="button" class="tag" data-filtro="{e(c)}" aria-pressed="false">'
                     f'{e(c)} <span class="tag-count">{n}</span></button>')

    if not posts:
        listado = '''    <div class="post-empty is-visible">
      <p>Todavía no publicamos ninguna nota. Muy pronto.</p>
    </div>'''
        filtros = ""
        destacada_html = ""
    else:
        filtros = f'''    <div class="tag-list" role="group" aria-label="Filtrar por categoría" data-reveal>
{chr(10).join(chips)}
    </div>'''
        destacada_html = f'''    <div class="post-grid" style="grid-template-columns:1fr; margin-top:0;" id="destacado">
{tarjeta(destacado, destacada=True)}
    </div>'''
        listado = f'''    <div class="post-grid" id="lista-posts">
{chr(10).join(tarjeta(p) for p in resto)}
    </div>
    <div class="post-empty" id="sin-resultados">
      <p>No hay notas en esa categoría.</p>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{titulo}</title>
<meta name="description" content="{desc}" />
{T.head_block("../", titulo, desc, "blog/index.html")}
</head>
<body>
{T.header_block("../", "blog")}

<section class="page-hero">
  <div class="bg-blob-wrap" aria-hidden="true">
    <div class="bg-blob" style="width:26rem; height:26rem; top:-8rem; right:-6rem;"></div>
    <div class="bg-blob b2" style="width:20rem; height:20rem; bottom:-10rem; left:-6rem;"></div>
  </div>
  <div class="container" style="position:relative; z-index:1;">
    <nav class="breadcrumb" aria-label="Migas de pan" data-reveal>
      <a href="../index.html">Inicio</a> <span>/</span> Blog
    </nav>
    <p class="eyebrow" data-reveal>Blog</p>
    <h1 class="glow-text" data-reveal style="--reveal-delay:.1s;">Plata clara, sin vueltas</h1>
    <p data-reveal style="--reveal-delay:.2s;">Notas sobre microcr&eacute;ditos, cheques, caudales, oro y cajas de seguridad. Lo que necesit&aacute;s saber antes de decidir.</p>
  </div>
</section>

<section class="section" style="padding-top:1.5rem;">
  <div class="container">
{destacada_html}
{filtros}
{listado}
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <div class="card glass max-34" data-reveal style="margin-inline:auto; text-align:center;">
      <div class="icon-badge animate-pulse-glow" style="margin-inline:auto;"><svg viewBox="0 0 24 24" fill="none" stroke="#09FED5" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 1 1-3.6-6.9L21 3v5h-5"/><path d="M8 11h.01M12 11h.01M16 11h.01"/></svg></div>
      <h2 style="font-size:1.25rem;">&iquest;Te qued&oacute; una duda?</h2>
      <p class="muted mt-1">Escribinos por WhatsApp y te la respondemos sin compromiso.</p>
      <a href="{T.WA}" class="btn btn-brand mt-2" target="_blank" rel="noopener">Hablanos</a>
    </div>
  </div>
</section>

{T.footer_block("../")}

{T.whatsapp_block()}

<script src="../js/main.js"></script>
</body>
</html>
'''


# --------------------------------------------------------------------------
# Sitemap
# --------------------------------------------------------------------------

def escribir_sitemap(posts):
    filas = [f'  <url><loc>{T.SITE}/{u}</loc><changefreq>monthly</changefreq>'
             f'<priority>{pr}</priority></url>' for u, pr in PAGINAS_FIJAS]
    for p in posts:
        filas.append(f'  <url><loc>{T.SITE}/blog/{p["slug"]}.html</loc>'
                     f'<lastmod>{p["fecha"].isoformat()}</lastmod>'
                     f'<changefreq>yearly</changefreq><priority>0.7</priority></url>')
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(filas) + "\n</urlset>\n")


# --------------------------------------------------------------------------

def main():
    if not os.path.isdir(POSTS_DIR):
        raise SystemExit(f"✗ No existe {POSTS_DIR}")

    archivos = sorted(f for f in os.listdir(POSTS_DIR)
                      if f.endswith(".md") and not f.startswith("_") and f != "LEEME.md")
    todos = [leer_post(os.path.join(POSTS_DIR, f)) for f in archivos]

    borradores = [p for p in todos if p["borrador"]]
    posts = sorted((p for p in todos if not p["borrador"]),
                   key=lambda p: p["fecha"], reverse=True)

    vistos = {}
    for p in posts:
        if p["slug"] in vistos:
            raise SystemExit(f"✗ Slug repetido '{p['slug']}': {vistos[p['slug']]} y {p['origen']}")
        vistos[p["slug"]] = p["origen"]

    # Limpia los .html viejos que ya no tienen su .md
    validos = {f"{p['slug']}.html" for p in posts} | {"index.html"}
    for f in os.listdir(BLOG_DIR):
        if f.endswith(".html") and f not in validos:
            os.remove(os.path.join(BLOG_DIR, f))
            print(f"  – borrado (ya no existe su .md): blog/{f}")

    for i, post in enumerate(posts):
        siguiente = posts[i - 1] if i > 0 else None          # más nuevo
        anterior = posts[i + 1] if i + 1 < len(posts) else None  # más viejo
        relacionados = [p for p in posts
                        if p is not post and p["categoria"] == post["categoria"]][:3]
        if len(relacionados) < 2:
            for p in posts:
                if p is not post and p not in relacionados:
                    relacionados.append(p)
                if len(relacionados) == 2:
                    break
        destino = os.path.join(BLOG_DIR, f"{post['slug']}.html")
        open(destino, "w", encoding="utf-8").write(
            render_post(post, anterior, siguiente, relacionados[:3]))
        print(f"  ✓ blog/{post['slug']}.html   ({post['minutos']} min · {post['categoria']})")

    open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8").write(render_index(posts))
    print(f"  ✓ blog/index.html   ({len(posts)} nota{'s' if len(posts) != 1 else ''})")

    escribir_home(posts)

    escribir_sitemap(posts)
    print("  ✓ sitemap.xml")

    if borradores:
        print("\n  Borradores sin publicar:")
        for b in borradores:
            print(f"    · {b['origen']}  —  {b['titulo']}")

    print("\nListo.")


if __name__ == "__main__":
    main()
