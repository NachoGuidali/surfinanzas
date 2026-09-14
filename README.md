# Sur Finanzas — sitio web

Sitio institucional de Sur Finanzas (Canning, Buenos Aires): inicio, servicios,
blog, nosotros y contacto, más un panel para publicar notas y editar el simulador
de créditos.

El sitio es HTML estático. Las partes que se repiten (menú, pie, servicios,
canal de WhatsApp, sucursal) salen de scripts en Python, así que un dato se
cambia en un solo lugar y se regenera en todas las páginas.

## Estructura

| Carpeta / archivo | Qué hay |
|---|---|
| `index.html`, `nosotros.html`, `contacto.html` | Páginas fijas |
| `servicios/` | Una página por servicio (generadas) |
| `blog/` | Notas publicadas (generadas); los originales en Markdown están en `blog/_posts/` |
| `css/`, `js/`, `assets/` | Estilos, scripts e imágenes |
| `tools/` | Generadores y fuentes de datos |
| `admin/` | Panel de administración (Flask) y archivos de despliegue |
| `mantenimiento.html` | Página para mostrar mientras se trabaja en el servidor |

## Dónde se cambia cada cosa

- **Teléfono, WhatsApp, canal, sucursal y redes:** `tools/empresa.py`
- **Servicios (textos, fotos, preguntas frecuentes, simulador por defecto):** `tools/servicios.py`
- **Menú, pie y bloques compartidos:** `tools/plantilla.py`
- **Notas del blog y tasa del simulador:** desde el panel

Después de tocar cualquiera de los archivos de `tools/`:

```bash
python3 tools/generar-servicios.py
python3 tools/actualizar-nav.py
python3 tools/generar-blog.py
```

## Levantarlo en local

```bash
# Sitio
python3 -m http.server 8080

# Panel (en otra terminal)
python3 -m venv .venv
source .venv/bin/activate
pip install -r admin/requirements.txt
python3 admin/usuarios.py agregar <usuario>
python3 admin/app.py
```

Las variables del panel están explicadas en `admin/.env.ejemplo`.

## Despliegue

La guía completa para el servidor (nginx, gunicorn, systemd y certificados) está
en [`admin/README.md`](admin/README.md), con los archivos en `admin/despliegue/`.

## Lo que no se versiona

`admin/.env` (claves), `admin/usuarios.json` (usuarios del panel), `datos/`
(mensajes del formulario y configuración del simulador) y `.venv/`. En el
servidor se crean de nuevo; nunca se copian desde una máquina de desarrollo.
