"""
Capa de contenido del panel.

Todo lo que toca archivos vive acá: leer y escribir los .md de las notas,
guardar imágenes y disparar el generador. No hay base de datos: los
archivos SON la base. Un backup es copiar blog/_posts/ y assets/blog/.
"""

import io
import os
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(RAIZ, "blog", "_posts")
IMG_DIR = os.path.join(RAIZ, "assets", "blog")
GENERADOR = os.path.join(RAIZ, "tools", "generar-blog.py")

# Dónde se guardan los datos que edita el panel (mensajes, config del
# simulador). Fuera del alcance público: nginx bloquea /datos/.
DATOS_DIR = os.environ.get("DATOS_DIR") or os.path.join(RAIZ, "datos")

CAMPOS = ("titulo", "resumen", "fecha", "categoria", "autor",
          "imagen", "destacado", "borrador")

MAX_IMAGEN_BYTES = 8 * 1024 * 1024
ANCHO_MAXIMO = 1600

sys.path.insert(0, os.path.join(RAIZ, "tools"))


class ErrorContenido(Exception):
    """Error esperable, con un mensaje que se le puede mostrar al usuario."""


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def slugificar(texto):
    """'Cheque: cómo cobrar' -> 'cheque-como-cobrar'"""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = texto.encode("ascii", "ignore").decode("ascii").lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return re.sub(r"-{2,}", "-", texto)[:80]


def _validar_nombre(nombre):
    """Evita que un nombre de archivo se escape de su carpeta."""
    if not nombre or "/" in nombre or "\\" in nombre or nombre.startswith("."):
        raise ErrorContenido("Nombre de archivo inválido.")
    if ".." in nombre:
        raise ErrorContenido("Nombre de archivo inválido.")
    return nombre


def ruta_post(nombre):
    _validar_nombre(nombre)
    if not nombre.endswith(".md"):
        raise ErrorContenido("Solo se pueden abrir archivos .md")
    ruta = os.path.realpath(os.path.join(POSTS_DIR, nombre))
    if os.path.dirname(ruta) != os.path.realpath(POSTS_DIR):
        raise ErrorContenido("Ruta fuera de la carpeta de notas.")
    return ruta


def _escapar(valor):
    return str(valor or "").replace("\\", "\\\\").replace('"', '\\"')


def es_nota(nombre):
    return (nombre.endswith(".md")
            and not nombre.startswith("_")
            and nombre != "LEEME.md")


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------

_generador = None
_servicios_mod = None


def _mod_generador():
    """Carga tools/generar-blog.py una sola vez y lo reusa."""
    global _generador
    if _generador is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("generador", GENERADOR)
        _generador = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_generador)
    return _generador


def _parsear(texto):
    return _mod_generador().parsear_encabezado(texto)


def leer(nombre):
    """Devuelve el diccionario de una nota a partir de su archivo."""
    ruta = ruta_post(nombre)
    if not os.path.exists(ruta):
        raise ErrorContenido("Esa nota no existe.")

    raw = open(ruta, encoding="utf-8").read().lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise ErrorContenido(f"El archivo {nombre} no tiene encabezado válido.")

    meta = _parsear(m.group(1))
    cuerpo = m.group(2).strip()

    try:
        fecha = datetime.date.fromisoformat(meta.get("fecha", ""))
    except ValueError:
        fecha = datetime.date.today()

    slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", nombre[:-3])

    return {
        "archivo": nombre,
        "slug": slug,
        "titulo": meta.get("titulo", ""),
        "resumen": meta.get("resumen", ""),
        "fecha": fecha,
        "categoria": meta.get("categoria", "Notas"),
        "autor": meta.get("autor", "Equipo Sur Finanzas"),
        "imagen": meta.get("imagen", ""),
        "destacado": meta.get("destacado", "").lower() in ("true", "si", "sí", "1"),
        "borrador": meta.get("borrador", "").lower() in ("true", "si", "sí", "1"),
        "cuerpo": cuerpo,
        "palabras": len(re.findall(r"\w+", cuerpo)),
    }


def listar():
    """Todas las notas, de la más nueva a la más vieja."""
    if not os.path.isdir(POSTS_DIR):
        return []
    notas = []
    for nombre in os.listdir(POSTS_DIR):
        if not es_nota(nombre):
            continue
        try:
            notas.append(leer(nombre))
        except ErrorContenido:
            continue
    return sorted(notas, key=lambda n: (n["fecha"], n["archivo"]), reverse=True)


def categorias():
    return sorted({n["categoria"] for n in listar() if n["categoria"]})


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------

def guardar(datos, archivo_original=None):
    """Escribe el .md. Si cambió la fecha o el slug, renombra el archivo."""
    titulo = (datos.get("titulo") or "").strip()
    if not titulo:
        raise ErrorContenido("La nota necesita un título.")

    try:
        fecha = datetime.date.fromisoformat(datos.get("fecha", ""))
    except ValueError:
        raise ErrorContenido("La fecha tiene que tener el formato AAAA-MM-DD.")

    slug = slugificar(datos.get("slug") or titulo)
    if not slug:
        raise ErrorContenido("No se pudo armar la URL a partir del título.")

    nombre = f"{fecha.isoformat()}-{slug}.md"
    destino = ruta_post(nombre)

    # Un slug repetido pisaría la página HTML de otra nota
    for otra in listar():
        if otra["archivo"] in (nombre, archivo_original):
            continue
        if otra["slug"] == slug and not otra["borrador"]:
            raise ErrorContenido(
                f"Ya hay otra nota publicada con la URL «{slug}». Cambiá el título o la URL.")

    ruta_anterior = ruta_post(archivo_original) if archivo_original else None
    if os.path.exists(destino) and destino != ruta_anterior:
        raise ErrorContenido(f"Ya existe un archivo llamado {nombre}.")

    def booleano(valor):
        return "true" if valor in (True, "true", "on", "1", 1) else "false"

    lineas = [
        f'titulo: "{_escapar(titulo)}"',
        f'resumen: "{_escapar(datos.get("resumen"))}"',
        f'fecha: {fecha.isoformat()}',
        f'categoria: "{_escapar(datos.get("categoria") or "Notas")}"',
        f'autor: "{_escapar(datos.get("autor") or "Equipo Sur Finanzas")}"',
        f'imagen: "{_escapar(datos.get("imagen"))}"',
        f'destacado: {booleano(datos.get("destacado"))}',
        f'borrador: {booleano(datos.get("borrador"))}',
    ]
    encabezado = "\n".join(lineas)

    cuerpo = (datos.get("cuerpo") or "").replace("\r\n", "\n").strip()
    open(destino, "w", encoding="utf-8").write(f"---\n{encabezado}\n---\n\n{cuerpo}\n")

    if ruta_anterior and ruta_anterior != destino and os.path.exists(ruta_anterior):
        os.remove(ruta_anterior)

    return nombre


def eliminar(nombre):
    ruta = ruta_post(nombre)
    if not os.path.exists(ruta):
        raise ErrorContenido("Esa nota no existe.")
    papelera = os.path.join(POSTS_DIR, "_papelera")
    os.makedirs(papelera, exist_ok=True)
    sello = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.move(ruta, os.path.join(papelera, f"{sello}-{nombre}"))


# ---------------------------------------------------------------------------
# Imágenes
# ---------------------------------------------------------------------------

def guardar_imagen(archivo_subido):
    """Valida, redimensiona y guarda una imagen en assets/blog/."""
    from PIL import Image, UnidentifiedImageError

    datos = archivo_subido.read(MAX_IMAGEN_BYTES + 1)
    if len(datos) > MAX_IMAGEN_BYTES:
        raise ErrorContenido("La imagen no puede pesar más de 8 MB.")
    if not datos:
        raise ErrorContenido("No llegó ninguna imagen.")

    # El tipo se decide por el contenido real, nunca por la extensión enviada
    try:
        im = Image.open(io.BytesIO(datos))
        im.verify()
        im = Image.open(io.BytesIO(datos))
    except (UnidentifiedImageError, OSError):
        raise ErrorContenido("El archivo no es una imagen válida.")

    if im.format not in ("JPEG", "PNG", "WEBP"):
        raise ErrorContenido("Formato no admitido. Usá JPG, PNG o WEBP.")

    im = im.convert("RGB")
    if im.width > ANCHO_MAXIMO:
        im = im.resize((ANCHO_MAXIMO, round(im.height * ANCHO_MAXIMO / im.width)),
                       Image.LANCZOS)

    base = slugificar(os.path.splitext(archivo_subido.filename or "imagen")[0]) or "imagen"
    os.makedirs(IMG_DIR, exist_ok=True)
    nombre = f"{base}.jpg"
    n = 2
    while os.path.exists(os.path.join(IMG_DIR, nombre)):
        nombre = f"{base}-{n}.jpg"
        n += 1

    im.save(os.path.join(IMG_DIR, nombre), "JPEG", quality=86, optimize=True)
    return f"assets/blog/{nombre}", (im.width, im.height)


def listar_imagenes():
    if not os.path.isdir(IMG_DIR):
        return []
    nombres = [f for f in os.listdir(IMG_DIR)
               if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    return sorted(f"assets/blog/{n}" for n in nombres)


# ---------------------------------------------------------------------------
# Generación del sitio
# ---------------------------------------------------------------------------

def render_markdown(texto):
    """Mismo render que usa el generador, para que la vista previa coincida."""
    import markdown
    return markdown.markdown(
        texto or "",
        extensions=["extra", "sane_lists", "smarty", "toc"],
        output_format="html5",
    )


def generar():
    """Corre tools/generar-blog.py. Devuelve (ok, salida)."""
    try:
        r = subprocess.run(
            [sys.executable, GENERADOR],
            cwd=RAIZ, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, "El generador tardó demasiado y se canceló."
    salida = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0, salida.strip()


# ---------------------------------------------------------------------------
# Simulador de cuotas
# ---------------------------------------------------------------------------

GENERADOR_SERVICIOS = os.path.join(RAIZ, "tools", "generar-servicios.py")
ARCHIVO_SIMULADOR = os.path.join(DATOS_DIR, "simulador.json")

LIMITES = {
    "tasa_mensual": (0.0, 1.0),          # 0% a 100% mensual
    "minimo": (1_000, 1_000_000_000),
    "maximo": (1_000, 1_000_000_000),
    "paso": (1_000, 100_000_000),
    "inicial": (1_000, 1_000_000_000),
}


def servicios_con_simulador():
    return _mod_servicios().con_simulador()


def _mod_servicios():
    import importlib.util
    global _servicios_mod
    if _servicios_mod is None:
        ruta = os.path.join(RAIZ, "tools", "servicios.py")
        spec = importlib.util.spec_from_file_location("servicios_sf", ruta)
        _servicios_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_servicios_mod)
    return _servicios_mod


def leer_simulador(archivo):
    """Configuración efectiva (default del código + lo guardado en el panel)."""
    mod = _mod_servicios()
    servicio = next((s for s in mod.SERVICIOS if s["archivo"] == archivo), None)
    if not servicio or not servicio.get("simulador"):
        raise ErrorContenido("Ese servicio no tiene simulador.")
    return servicio, mod.config_simulador(servicio)


def _entero(valor, campo, minimo, maximo):
    try:
        n = int(str(valor).replace(".", "").replace(" ", "").strip())
    except (TypeError, ValueError):
        raise ErrorContenido(f"«{campo}» tiene que ser un número entero.")
    if not (minimo <= n <= maximo):
        raise ErrorContenido(
            f"«{campo}» tiene que estar entre {minimo:,} y {maximo:,}".replace(",", ".") + ".")
    return n


def guardar_simulador(archivo, datos):
    """Valida y guarda la configuración. Devuelve la config final."""
    servicio, actual = leer_simulador(archivo)

    # Tasa: en el panel se carga como porcentaje (7,5), se guarda como 0.075
    bruto = str(datos.get("tasa_mensual", "")).replace("%", "").replace(",", ".").strip()
    try:
        tasa = float(bruto) / 100
    except (TypeError, ValueError):
        raise ErrorContenido("La tasa tiene que ser un número, por ejemplo 7,5.")
    lo, hi = LIMITES["tasa_mensual"]
    if not (lo <= tasa <= hi):
        raise ErrorContenido("La tasa mensual tiene que estar entre 0% y 100%.")

    minimo = _entero(datos.get("minimo"), "Monto mínimo", *LIMITES["minimo"])
    maximo = _entero(datos.get("maximo"), "Monto máximo", *LIMITES["maximo"])
    paso = _entero(datos.get("paso"), "Paso", *LIMITES["paso"])
    inicial = _entero(datos.get("inicial"), "Monto inicial", *LIMITES["inicial"])

    if minimo >= maximo:
        raise ErrorContenido("El monto mínimo tiene que ser menor que el máximo.")
    if paso > (maximo - minimo):
        raise ErrorContenido("El paso no puede ser más grande que el rango de montos.")
    if not (minimo <= inicial <= maximo):
        raise ErrorContenido("El monto inicial tiene que estar dentro del rango.")

    crudo = str(datos.get("plazos", "")).replace(" ", "")
    try:
        plazos = sorted({int(p) for p in crudo.split(",") if p})
    except ValueError:
        raise ErrorContenido("Los plazos son números separados por comas. Ej: 3,6,12,24")
    if not plazos:
        raise ErrorContenido("Cargá al menos un plazo.")
    if len(plazos) > 10:
        raise ErrorContenido("Como mucho 10 plazos: más no entran bien en pantalla.")
    if any(p < 1 or p > 120 for p in plazos):
        raise ErrorContenido("Cada plazo tiene que estar entre 1 y 120 meses.")

    try:
        plazo_inicial = int(datos.get("plazo_inicial"))
    except (TypeError, ValueError):
        plazo_inicial = plazos[0]
    if plazo_inicial not in plazos:
        raise ErrorContenido("El plazo destacado tiene que ser uno de los plazos cargados.")

    config = {
        "tasa_mensual": round(tasa, 6),
        "minimo": minimo,
        "maximo": maximo,
        "paso": paso,
        "inicial": inicial,
        "plazos": plazos,
        "plazo_inicial": plazo_inicial,
    }

    os.makedirs(DATOS_DIR, exist_ok=True)
    todo = {}
    if os.path.exists(ARCHIVO_SIMULADOR):
        try:
            with open(ARCHIVO_SIMULADOR, encoding="utf-8") as fh:
                todo = json.load(fh)
        except ValueError:
            todo = {}
    todo[archivo] = config

    tmp = ARCHIVO_SIMULADOR + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(todo, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, ARCHIVO_SIMULADOR)

    return config


def cuota(capital, tasa, plazo):
    """Sistema francés: cuota fija. Con tasa 0 es capital dividido plazo."""
    if plazo <= 0:
        return 0.0
    if tasa <= 0:
        return capital / plazo
    return capital * tasa / (1 - (1 + tasa) ** -plazo)


def generar_servicios():
    """Corre tools/generar-servicios.py. Devuelve (ok, salida)."""
    try:
        r = subprocess.run(
            [sys.executable, GENERADOR_SERVICIOS],
            cwd=RAIZ, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, "El generador de servicios tardó demasiado y se canceló."
    salida = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0, salida.strip()


def regenerar_todo():
    """Servicios + blog. Devuelve (ok, salida combinada)."""
    ok1, s1 = generar_servicios()
    ok2, s2 = generar()
    return ok1 and ok2, (s1 + "\n" + s2).strip()
