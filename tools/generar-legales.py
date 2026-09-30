#!/usr/bin/env python3
"""
Genera terminos.html y privacidad.html.

⚠️ BORRADOR. Los textos de acá son una base genérica, armada a partir de lo
que el sitio realmente hace (formulario de contacto, WhatsApp, simulador,
medición de visitas). NO son asesoramiento legal: antes de publicar los tiene
que revisar un abogado, sobre todo la parte de datos personales y la de
servicios financieros.

Para cambiar un texto, editalo en CONTENIDO y volvé a correr:

    python3 tools/generar-legales.py

El menú y el pie se reaplican después con:  python3 tools/actualizar-nav.py
"""

import os
import sys
import html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantilla as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ACTUALIZADO = "23 de septiembre de 2026"
RAZON_SOCIAL = "Sur Finanzas Group S.A."
CUIT = "30-71740402-1"
DOMICILIO = "Seguí 776, Adrogué, Provincia de Buenos Aires"
MAIL_LEGALES = "Legales@surfinanzas.com.ar"
MAIL_INFO = "Info@surfinanzas.com.ar"


def p(texto):
    return f"<p>{texto}</p>"


def lista(items):
    li = "\n".join(f"      <li>{i}</li>" for i in items)
    return f"<ul>\n{li}\n    </ul>"


TERMINOS = [
    ("Quiénes somos", [
        p("Al navegar el sitio aceptás estos términos. Si no estás de acuerdo con "
          "alguno, te pedimos que no lo uses."),
    ]),
    ("Para qué sirve este sitio", [
        p("El sitio es informativo: describe los servicios de Sur Finanzas y ofrece "
          "canales de contacto. Nada de lo publicado constituye una oferta, una "
          "promesa de crédito ni asesoramiento financiero, legal o impositivo."),
        p("No se venden productos ni se contratan servicios en línea. Las consultas "
          "se derivan a WhatsApp, al correo o a la sucursal, y cada operación se "
          "formaliza por los canales y con la documentación que se informen en cada caso."),
    ]),
    ("Simulador de cuotas", [
        p("El simulador de microcréditos es una herramienta orientativa. Calcula un "
          "valor estimado a partir de los parámetros cargados en el sitio y puede no "
          "coincidir con la propuesta final."),
        p("Las condiciones definitivas —monto, plazo, tasa, gastos e impuestos— se "
          "determinan en la evaluación crediticia y se informan por escrito antes de "
          "cualquier firma. El resultado del simulador no obliga a Sur Finanzas ni "
          "implica aprobación."),
    ]),
    ("Servicios sujetos a evaluación y normativa", [
        p("El otorgamiento de créditos, el alquiler de cajas de seguridad, el "
          "transporte de caudales y los demás servicios están sujetos a evaluación "
          "previa, a la presentación de documentación y al cumplimiento de la "
          "normativa vigente, incluida la de prevención de lavado de activos y "
          "financiación del terrorismo."),
        p("Sur Finanzas puede rechazar una solicitud sin expresar causa."),
    ]),
    ("Uso del sitio", [
        p("Podés usar el sitio para informarte y contactarnos. No está permitido:"),
        lista([
            "usar el sitio con fines ilícitos o contrarios a estos términos;",
            "intentar acceder a áreas restringidas, alterar el contenido o afectar su funcionamiento;",
            "usar sistemas automatizados que generen tráfico o consultas masivas;",
            "enviar por el formulario datos de terceros sin su consentimiento.",
        ]),
    ]),
    ("Contenidos y marcas", [
        p("Los textos, imágenes, ilustraciones, videos, el logo y el nombre "
          "Sur Finanzas pertenecen a Sur Finanzas o se usan con autorización. "
          "No pueden reproducirse ni modificarse sin permiso escrito, salvo la "
          "cita de notas del blog con mención de la fuente y enlace."),
    ]),
    ("Enlaces y contenidos de terceros", [
        p("El sitio enlaza o incrusta servicios de terceros, como WhatsApp, YouTube "
          "y los mapas de Google. Esos servicios se rigen por sus propios términos y "
          "políticas de privacidad, y Sur Finanzas no responde por su contenido ni "
          "por su disponibilidad."),
    ]),
    ("Disponibilidad y cambios", [
        p("Procuramos que el sitio esté siempre disponible y actualizado, pero puede "
          "haber interrupciones por mantenimiento o por causas ajenas. Las "
          "características, condiciones y valores publicados pueden cambiar sin "
          "aviso previo."),
        p("También podemos modificar estos términos. La versión vigente es la "
          "publicada en esta página, con su fecha de actualización."),
    ]),
    ("Responsabilidad", [
        p("Sur Finanzas no responde por daños derivados del uso del sitio, de la "
          "imposibilidad de usarlo o de decisiones tomadas únicamente sobre la base "
          "de la información publicada, que es de carácter general."),
    ]),
    ("Datos personales", [
        p('El tratamiento de los datos que nos dejás está explicado en la '
          '<a href="privacidad.html">Política de privacidad</a>, que forma parte de '
          'estos términos.'),
    ]),
    ("Ley aplicable y jurisdicción", [
        p("Estos términos se rigen por las leyes de la República Argentina. Ante "
          "cualquier controversia se aplican los tribunales ordinarios que "
          "correspondan al domicilio legal de Sur Finanzas, sin perjuicio de los "
          "derechos que la normativa de defensa del consumidor reconozca al "
          "consumidor de elegir otra jurisdicción."),
    ]),
    ("Contacto", [
        p(f'Por consultas sobre estos términos, escribinos a '
          f'<a href="mailto:{MAIL_LEGALES}">{MAIL_LEGALES}</a> o a '
          f'<a href="mailto:{MAIL_INFO}">{MAIL_INFO}</a>.'),
    ]),
]

PRIVACIDAD = [
    ("Quién es responsable de tus datos", [
        p(f'Para cualquier tema de privacidad podés escribir a '
          f'<a href="mailto:{MAIL_LEGALES}">{MAIL_LEGALES}</a>.'),
    ]),
    ("Qué datos recibimos", [
        p("<strong>Los que nos dejás vos.</strong> Si usás el formulario de contacto: "
          "nombre, correo electrónico, el área elegida y el mensaje. Si nos escribís "
          "por WhatsApp o por correo: los datos que incluyas en esa conversación."),
        p("<strong>Los que genera tu visita.</strong> Datos técnicos de navegación, "
          "como las páginas que abrís, la fecha y hora, el tipo de dispositivo y "
          "navegador, y una versión reducida de tu dirección IP. Los usamos de forma "
          "agregada, para saber qué contenidos son útiles."),
        p("No pedimos ni necesitamos datos sensibles para usar el sitio. Tampoco hace "
          "falta que cargues datos de terceros: si lo hacés, tenés que contar con su "
          "consentimiento."),
    ]),
    ("Para qué los usamos", [
        lista([
            "responder tu consulta y darte información sobre los servicios;",
            "contactarte por el mismo canal por el que nos escribiste;",
            "mejorar el sitio y sus contenidos;",
            "cumplir con obligaciones legales y regulatorias.",
        ]),
        p("No usamos tus datos para publicidad de terceros ni los vendemos."),
    ]),
    ("Con quién los compartimos", [
        p("Solo con quienes necesitan intervenir para prestar el servicio: el "
          "proveedor de alojamiento del sitio y el servicio de correo con el que se "
          "envían los avisos. También con autoridades, cuando una norma o una orden "
          "judicial lo exija."),
    ]),
    ("Cuánto tiempo los guardamos", [
        p("Conservamos las consultas por el tiempo necesario para responderlas y "
          "dejar registro de la gestión, y luego durante el plazo que exijan las "
          "normas aplicables. Después se eliminan o se anonimizan."),
    ]),
    ("Cookies y medición de visitas", [
        p("El sitio usa una herramienta propia de medición para contar visitas y ver "
          "qué páginas se leen. No la usamos para identificarte ni para seguirte por "
          "otros sitios."),
        p("Los contenidos incrustados de terceros —los videos de YouTube y el mapa de "
          "Google— pueden instalar sus propias cookies cuando los usás. Podés "
          "bloquear o borrar las cookies desde la configuración de tu navegador."),
    ]),
    ("Tus derechos", [
        p("Podés pedirnos acceder a tus datos, actualizarlos, rectificarlos o "
          f'suprimirlos. Escribinos a <a href="mailto:{MAIL_LEGALES}">{MAIL_LEGALES}</a> '
          "indicando tu pedido; para proteger tus datos podemos pedirte que acredites "
          "tu identidad."),
        p("<em>El titular de los datos personales tiene la facultad de ejercer el "
          "derecho de acceso a los mismos en forma gratuita a intervalos no inferiores "
          "a seis meses, salvo que se acredite un interés legítimo al efecto, conforme "
          "lo establecido en el artículo 14, inciso 3 de la Ley N° 25.326.</em>"),
        p("<em>La Agencia de Acceso a la Información Pública, en su carácter de órgano "
          "de control de la Ley N° 25.326, tiene la atribución de atender las denuncias "
          "y reclamos que interpongan quienes resulten afectados en sus derechos por "
          "incumplimiento de las normas vigentes en materia de protección de datos "
          "personales.</em>"),
    ]),
    ("Seguridad", [
        p("El sitio se sirve cifrado (HTTPS) y el acceso a las consultas recibidas "
          "está restringido a las personas autorizadas de Sur Finanzas. Ningún sistema "
          "es infalible, pero trabajamos para reducir los riesgos."),
    ]),
    ("Menores de edad", [
        p("El sitio está dirigido a personas mayores de 18 años. No recolectamos "
          "datos de menores en forma consciente."),
    ]),
    ("Cambios en esta política", [
        p("Si cambiamos la forma en que tratamos los datos, vamos a publicar la nueva "
          "versión en esta página, con su fecha de actualización."),
    ]),
]

CONTENIDO = {
    "terminos.html": {
        "titulo_seo": "Términos y condiciones — Sur Finanzas",
        "descripcion": "Condiciones de uso del sitio de Sur Finanzas: alcance de la "
                       "información publicada, simulador, contenidos y contacto.",
        "eyebrow": "Legales",
        "h1": "Términos y condiciones",
        "bajada": "Las reglas de uso de este sitio y el alcance de lo que publicamos.",
        "secciones": TERMINOS,
    },
    "privacidad.html": {
        "titulo_seo": "Política de privacidad — Sur Finanzas",
        "descripcion": "Qué datos personales recibe el sitio de Sur Finanzas, para qué "
                       "se usan, cuánto se guardan y cómo ejercer tus derechos.",
        "eyebrow": "Legales",
        "h1": "Política de privacidad",
        "bajada": "Qué datos nos dejás, qué hacemos con ellos y cómo pedir que los "
                  "borremos.",
        "secciones": PRIVACIDAD,
    },
}


def render(archivo, d):
    e = lambda t: html.escape(t, quote=True)
    secciones = "\n\n".join(
        f'      <h2>{e(titulo)}</h2>\n      ' + "\n      ".join(bloques)
        for titulo, bloques in d["secciones"])

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(d["titulo_seo"])}</title>
<meta name="description" content="{e(d["descripcion"])}" />
{T.head_block("", e(d["titulo_seo"]), e(d["descripcion"]), archivo)}
</head>
<body>
{T.header_block("", "")}

<section class="page-hero">
  <div class="bg-blob-wrap" aria-hidden="true">
    <div class="bg-blob" style="width:26rem; height:26rem; top:-8rem; right:-6rem;"></div>
    <div class="bg-blob b2" style="width:20rem; height:20rem; bottom:-10rem; left:-6rem;"></div>
  </div>
  <div class="container" style="position:relative; z-index:1;">
    <nav class="breadcrumb" aria-label="Migas de pan" data-reveal>
      <a href="index.html">Inicio</a> <span>/</span> {e(d["h1"])}
    </nav>
    <p class="eyebrow" data-reveal>{e(d["eyebrow"])}</p>
    <h1 class="glow-text" data-reveal style="--reveal-delay:.1s;">{e(d["h1"])}</h1>
    <p data-reveal style="--reveal-delay:.2s;">{e(d["bajada"])}</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="post-layout prose" data-reveal>
      <p class="muted chico">Última actualización: {ACTUALIZADO}</p>

{secciones}
    </div>
  </div>
</section>

{T.footer_block("")}

{T.whatsapp_block()}

<script src="js/main.js"></script>
</body>
</html>
'''


if __name__ == "__main__":
    for archivo, d in CONTENIDO.items():
        with open(os.path.join(ROOT, archivo), "w", encoding="utf-8") as fh:
            fh.write(render(archivo, d))
        print(f"  ✓ {archivo}   ({len(d['secciones'])} secciones)")
    print("\nListo. Si tocaste el menú o el pie, corré también:"
          "\n  python3 tools/actualizar-nav.py")
