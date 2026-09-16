#!/usr/bin/env python3
"""
Reaplica head / header / footer / botón de WhatsApp en las páginas fijas
(inicio, nosotros, contacto y las de servicios) usando tools/plantilla.py.

Corrélo cada vez que toques el menú o el pie en plantilla.py:

    python3 tools/actualizar-nav.py

El blog se regenera aparte con:  python3 tools/generar-blog.py
"""

import os
import re
import sys
import html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantilla as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Bloques que salen de plantilla.py y viven dentro de una página, entre
# marcadores HTML. Si el marcador no está, se avisa y se sigue.
#   ruta del archivo -> {nombre del marcador: función que lo genera}
BLOQUES = {
    "index.html": {"canal-banda": lambda: T.canal_banda()},
    "contacto.html": {
        "canal-tarjeta": lambda: T.canal_tarjeta(),
        "redes": lambda: T.redes_banner(),
        "sucursal": lambda: T.sucursal_block(
            eyebrow="La sucursal", cta="Hablanos", fondo="normal",
            wa=T.WA_SUCURSAL),
    },
    "nosotros.html": {
        "sucursal": lambda: T.sucursal_block(
            eyebrow="Dónde estamos", cta="Hablanos"),
    },
}


def reemplazar_bloque(texto, marca, contenido):
    """Reemplaza lo que haya entre <!-- marca:inicio --> y <!-- marca:fin -->.

    Devuelve (texto, encontrado). Deja los marcadores en su lugar para que
    la próxima corrida los vuelva a encontrar.
    """
    ini, fin = f"<!-- {marca}:inicio -->", f"<!-- {marca}:fin -->"
    patron = re.compile(re.escape(ini) + r".*?" + re.escape(fin), re.S)
    if not patron.search(texto):
        return texto, False
    return patron.sub(lambda _: f"{ini}\n{contenido}\n    {fin}", texto, count=1), True


PAGINAS = {
    "index.html": ("", "inicio"),
    "nosotros.html": ("", "nosotros"),
    "contacto.html": ("", "contacto"),
}
for href, _ in T.SERVICES:
    PAGINAS[href] = ("../", "servicios")


def procesar(rel, prefix, active):
    path = os.path.join(ROOT, rel)
    s = open(path, encoding="utf-8").read()

    title = re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip()
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = m.group(1) if m else ""

    nuevo_head = T.head_block(prefix, html.escape(title, quote=True),
                              html.escape(desc, quote=True), rel)
    s, n = re.subn(
        r'<link rel="icon"[\s\S]*?<script>document\.documentElement\.classList\.add\("js"\);</script>',
        lambda _: nuevo_head, s, count=1)
    assert n == 1, f"head no encontrado en {rel}"

    s, n = re.subn(
        r'<div class="scroll-progress"[\s\S]*?<div class="nav-spacer"[^>]*></div>',
        lambda _: T.header_block(prefix, active), s, count=1)
    assert n == 1, f"header no encontrado en {rel}"

    s, n = re.subn(r'<footer class="footer">[\s\S]*?</footer>',
                   lambda _: T.footer_block(prefix), s, count=1)
    assert n == 1, f"footer no encontrado en {rel}"

    s, n = re.subn(r'<a href="[^"]*" class="whatsapp-float"[\s\S]*?</a>',
                   lambda _: T.whatsapp_block(), s, count=1)
    assert n == 1, f"whatsapp no encontrado en {rel}"

    avisos = []
    for marca, generar in BLOQUES.get(rel, {}).items():
        s, ok = reemplazar_bloque(s, marca, generar())
        if not ok:
            avisos.append(marca)

    open(path, "w", encoding="utf-8").write(s)
    extra = f"   (faltan marcadores: {', '.join(avisos)})" if avisos else ""
    print(f"  ✓ {rel}{extra}")


if __name__ == "__main__":
    for rel, (prefix, active) in PAGINAS.items():
        procesar(rel, prefix, active)
    print("\nListo. Acordate de correr también:  python3 tools/generar-blog.py")
