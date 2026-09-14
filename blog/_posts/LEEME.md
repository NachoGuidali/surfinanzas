# Cómo publicar una nota en el blog

Hay tres formas. Elegí la que te resulte más cómoda.

---

## Opción A — El panel web (la más simple)

Entrás a `panel.surfinanzas.com.ar`, iniciás sesión y cargás la nota desde el
navegador: editor con vista previa, subida de imágenes y botón de publicar.
No hace falta tocar archivos ni correr comandos.

Instalación y uso del panel: ver `admin/README.md`.

Las otras dos opciones siguen funcionando igual — el panel escribe exactamente
los mismos archivos que vas a ver acá abajo.

---

## Opción B — Escribir el Markdown a mano

Si preferís trabajar en tu editor de texto y correr el generador vos.

### 1. Creá el archivo

En esta misma carpeta (`blog/_posts/`), creá un archivo con este formato de nombre:

```
2026-09-15-titulo-corto-con-guiones.md
```

La fecha del nombre solo sirve para ordenar los archivos. El nombre después
de la fecha se convierte en la URL: el ejemplo de arriba queda como
`surfinanzas.com.ar/blog/titulo-corto-con-guiones.html`.

### 2. Pegá este encabezado y editalo

```markdown
---
titulo: El título que se ve grande arriba de todo
resumen: Una o dos frases. Es lo que se lee en la tarjeta del listado y lo que aparece al compartir en WhatsApp.
fecha: 2026-09-15
categoria: Cheques
autor: Equipo Sur Finanzas
imagen: assets/blog/cheques.jpg
destacado: false
borrador: false
---

Acá arranca el texto de la nota.
```

Qué significa cada campo:

| Campo | Obligatorio | Para qué sirve |
|---|---|---|
| `titulo` | sí | Título de la nota |
| `fecha` | sí | Formato `AAAA-MM-DD`. Ordena el listado |
| `resumen` | recomendado | Texto de la tarjeta y de las redes sociales |
| `categoria` | no | Crea el filtro del listado. Si no ponés nada queda "Notas" |
| `autor` | no | Por defecto "Equipo Sur Finanzas" |
| `imagen` | no | Portada. Si la dejás vacía se usa un fondo de marca con el isotipo |
| `destacado` | no | `true` pone la nota grande arriba de todo. Usá una sola por vez |
| `borrador` | no | `true` = no se publica. Sirve para dejar algo a medio escribir |

### 3. Escribí el cuerpo

Markdown básico, es todo lo que necesitás:

```markdown
## Un subtítulo

Un párrafo normal. Podés poner **negrita**, *cursiva* y
[un enlace](https://www.surfinanzas.com.ar/contacto.html).

- Un ítem de lista
- Otro ítem

1. Una lista numerada
2. Segundo paso

> Una cita destacada, queda con el borde turquesa.

![Texto alternativo](../assets/blog/mi-imagen.jpg)
```

### 4. Generá el sitio

Desde la carpeta raíz del proyecto:

```bash
python3 tools/generar-blog.py
```

Eso escribe la página de la nota, rehace el listado y actualiza el `sitemap.xml`.

La primera vez, si te dice que falta `markdown`:

```bash
pip install markdown
```

---

## Opción C — Editar el HTML a mano

Si no querés usar el generador, el blog funciona igual: son páginas HTML
comunes. Duplicá cualquier archivo de `blog/` (por ejemplo
`como-funciona-el-descuento-de-cheques.html`), renombralo, y editá el texto.

Después agregá la tarjeta a mano en `blog/index.html`, copiando un bloque
`<a class="post-card" ...>` existente.

**Ojo:** si más adelante corrés `tools/generar-blog.py`, el generador rehace
`blog/index.html` y borra los `.html` que no tengan su `.md` correspondiente.
Elegí una de las dos formas y quedate con esa.

---

## Portadas

Las tres imágenes de `assets/blog/` se generaron a medida con los colores de
la marca. Si querés usar fotos propias:

- Tamaño ideal: **1280 × 720** (16:9)
- Formato `.jpg`, hasta ~200 KB
- Guardalas en `assets/blog/` y referencialas desde el encabezado:
  `imagen: assets/blog/nombre-del-archivo.jpg`

Si no ponés imagen, la nota usa un fondo de marca con el isotipo. Queda
prolijo, así que no es obligatorio conseguir una foto para publicar.

---

## Otros comandos

```bash
python3 tools/generar-blog.py      # regenera el blog y el sitemap
python3 tools/actualizar-nav.py    # reaplica menú y pie en las páginas fijas
```

Si tocás el menú o el pie de página, editalos en `tools/plantilla.py` y corré
los dos comandos. Así el cambio se propaga a todas las páginas de una.

---

## Nota sobre esta carpeta

`blog/_posts/` son los **archivos fuente**, no se publican. El guion bajo del
nombre marca eso. Podés dejarlos fuera del zip de deploy sin problema.
