"""
Los servicios de Sur Finanzas — fuente única de verdad.

De acá salen el menú, el pie de página, las tarjetas del inicio y las
páginas de cada servicio. Si cambia un servicio, se cambia SOLO acá y
después se corre:

    python3 tools/generar-servicios.py
    python3 tools/actualizar-nav.py
    python3 tools/generar-blog.py

Campos de cada servicio:
    archivo       nombre del .html dentro de servicios/
    nombre        cómo aparece en el menú y el pie
    titulo        el título grande de la página (h1)
    gancho        frase corta en negrita, arriba del resumen en el inicio
    resumen       una línea: tarjeta del inicio + meta description
    descripcion   el párrafo del encabezado de la página
    puntos        (título, detalle) — las tarjetas del cuerpo
    cta           texto del botón
    wa            texto con el que se abre el WhatsApp
    proximamente  True = todavía no está disponible
    imagen        foto del encabezado, ej: "assets/servicios/cheques.jpg".
                  Vacío = se muestra un placeholder. Ideal 1200x900 px (4:3).
    imagen_alt    descripción de la foto para lectores de pantalla y SEO
"""

import json as _json
import os as _os

import empresa

_RAIZ = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATOS = _os.environ.get("DATOS_DIR") or _os.path.join(_RAIZ, "datos")
ARCHIVO_SIMULADOR = _os.path.join(_DATOS, "simulador.json")


def config_simulador(servicio):
    """Configuración efectiva del simulador de un servicio.

    Los valores de este archivo son el punto de partida. Si el panel guardó
    algo en datos/simulador.json, eso manda. Así un deploy nuevo funciona sin
    configurar nada, y lo que se toca desde el panel sobrevive a los deploys.
    """
    base = servicio.get("simulador")
    if not base:
        return None
    config = dict(base)
    try:
        with open(ARCHIVO_SIMULADOR, encoding="utf-8") as fh:
            guardado = _json.load(fh).get(servicio["archivo"], {})
        config.update({k: v for k, v in guardado.items() if k in base})
    except (OSError, ValueError, AttributeError):
        pass          # sin override, o archivo ilegible: seguimos con el default
    return config


def con_simulador():
    """Los servicios que tienen simulador (para listarlos en el panel)."""
    return [s for s in SERVICIOS if s.get("simulador")]


# --- Íconos (trazo de 1.6, mismo estilo en todos) --------------------------

_ICO = {
    "oro": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v9M9 9.8c0-1.1 1.2-2 2.7-2s2.7.7 2.7 1.8c0 2.4-5.4 1.2-5.4 3.6 0 1.1 1.2 1.9 2.7 1.9s2.7-.8 2.7-1.9"/>',
    "cheques": '<path d="M3 6h18v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6Z"/><path d="M3 10h18"/><path d="M6 14h5"/><path d="M15 16.5l1.6 1.6L20 14.8"/>',
    "microcreditos": '<path d="M12 21c-4-1.5-7-4.5-7-9V6l7-3 7 3v6"/><path d="M12 12v5"/><path d="M9.6 13.4c0-.8.9-1.4 2-1.4"/><circle cx="17.5" cy="17.5" r="3.5"/><path d="M17.5 16v3M16 17.5h3"/>',
    "recaudadora": '<rect x="3" y="10" width="18" height="10" rx="2"/><path d="M7 10V8.5a5 5 0 0 1 10 0V10"/><path d="M12 13.5v3"/><path d="M8 3.5l1.6 2M16 3.5l-1.6 2"/>',
    "pagos": '<rect x="2.5" y="6" width="15" height="12" rx="2"/><path d="M2.5 10h15"/>'
             '<path d="M6 14h3"/>'
             '<path d="M19.5 9.5a4.5 4.5 0 0 1 0 5"/><path d="M21.8 7.2a8 8 0 0 1 0 9.6"/>',
    "cajas": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="12" cy="12" r="4.2"/><circle cx="12" cy="12" r="0.8" fill="currentColor"/><path d="M12 8v.8M12 15.2V16M8 12h.8M15.2 12H16"/>',
    "caudales": '<rect x="1" y="6" width="13" height="10" rx="1"/><path d="M14 9h4l3 3v4h-7z"/><circle cx="6" cy="18" r="1.6"/><circle cx="17.5" cy="18" r="1.6"/><path d="M5 10h5"/>',
    "digitales": '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M10.5 10.5h3M10.5 13.5h3"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    "ecommerce": '<path d="M3 4h2l2.2 11.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.2L21 8H6"/><circle cx="9.5" cy="20" r="1.4"/><circle cx="17.5" cy="20" r="1.4"/>',
}


def icono(clave, extra=""):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="#09FED5" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICO[clave]}</svg>')


# --- Los ocho servicios, en el orden en que se muestran --------------------

SERVICIOS = [
    {
        "archivo": "microcreditos.html",
        "nombre": "Microcréditos para emprendedores",
        "nombre_corto": "Microcréditos",
        "icono": "microcreditos",
        "imagen": "",
        "imagen_alt": "",
        "titulo": "El crédito que te banca",
        "gancho": "Requisitos mínimos, aprobación rápida.",
        "resumen": "Financiación ágil para mercadería, herramientas o capital de trabajo.",
        "descripcion": "Líneas de financiación ágiles para compra de mercadería, herramientas "
                       "o capital de trabajo. Requisitos mínimos y aprobación rápida.",
        # La grilla genérica de "En detalle" queda cubierta por las secciones
        # de abajo, que son más específicas.
        "puntos": [],

        "publico": {
            "titulo": "Para quién es este crédito",
            "bajada": "Si tu negocio es real, te bancamos.",
            "items": [
                "Comercios y PyMEs que necesitan capital para stock o insumos "
                "antes de una temporada fuerte.",
                "Negocios que quieren reformar o ampliar el local.",
                "Emprendimientos con operación real, aunque no tengan historial "
                "bancario prolijo.",
            ],
        },

        "proceso": {
            "titulo": "El proceso",
            "bajada": "En 3 pasos, sin letra chica.",
            "pasos": [
                ("Nos escribís por WhatsApp",
                 "Contás qué necesitás y cuánto."),
                ("Evaluamos tu negocio",
                 "Por videollamada o visita al local, sin Veraz como filtro."),
                ("Recibís el desembolso",
                 "Con acompañamiento de educación financiera incluido."),
            ],
        },

        "faq": {
            "titulo": "Preguntas frecuentes",
            "bajada": "Lo que más nos preguntan.",
            "preguntas": [
                ("¿Necesito garantía?",
                 "Depende del monto y de la evaluación — se conversa caso por caso, "
                 "no hay una regla única."),
                ("¿Cuánto tarda la evaluación?",
                 "Días, no semanas — por eso evaluamos con videollamada o visita, "
                 "no con formularios que se acumulan."),
                ("¿Puedo cancelar antes de tiempo?",
                 "Sí, se conversa en la propuesta inicial."),
            ],
        },
        "cta": "Pedí tu microcrédito",
        "wa": "Hola Sur Finanzas, quiero pedir un microcrédito para mi emprendimiento.",

        # ⚠️ VALORES DE EJEMPLO — reemplazar por los reales antes de publicar.
        # La tasa de acá sale en pantalla: si no es la que cobran, cambiala.
        "simulador": {
            "minimo": 100_000,
            "maximo": 3_000_000,
            "paso": 50_000,
            "inicial": 500_000,
            "plazos": [3, 6, 9, 12, 18, 24],
            "plazo_inicial": 12,
            "tasa_mensual": 0.075,      # 7,5% mensual — PLACEHOLDER
        },
    },
    {
        "archivo": "cheques-y-echeques.html",
        "nombre": "Compra y gestión de cheques y Echeq",
        "nombre_corto": "Cheques y Echeq",
        "icono": "cheques",
        "imagen": "",
        "imagen_alt": "",
        "titulo": "Convertí tus cheques en plata hoy",
        "gancho": "Liquidez inmediata para tu negocio.",
        "resumen": "Descuento y liquidación de cheques físicos y electrónicos, con tasas preferenciales.",
        "descripcion": "Descuento y liquidación ágil de cheques físicos y electrónicos. "
                       "Tasas preferenciales de mercado, acreditación rápida y gestión integral "
                       "para darle liquidez inmediata a tu negocio.",
        # El contenido vive en las secciones de abajo, más específicas que la
        # grilla genérica de "En detalle".
        "puntos": [],
        "orden": ["proceso", "secciones", "publico", "app", "video"],

        "proceso": {
            "titulo": "Cómo funciona",
            "bajada": "Tu cheque, activo en minutos.",
            "pasos": [
                ("Cargá tu cheque",
                 "Físico o e-cheque, desde la App Sur Finanzas o mandándolo por WhatsApp."),
                ("Te confirmamos la tasa en el momento",
                 "Sin sorpresas después — la tasa que te damos es la que se aplica."),
                ("Acreditamos en tu cuenta en minutos",
                 "No en días. La operación se cierra en el mismo contacto."),
            ],
        },

        "secciones": [
            {
                "eyebrow": "Qué operamos",
                "titulo": "Qué cheques operamos",
                "bajada": "De cualquier banco, propios o de terceros.",
                "texto": "Cheques físicos y e-cheques de cualquier banco, propios o de "
                         "terceros. No hay lista cerrada de libradores aceptados — se "
                         "evalúa cada cheque puntualmente.",
                "tarjetas": [
                    ("Cheques físicos", "De cualquier banco del país."),
                    ("E-cheques", "Electrónicos, propios o de terceros."),
                ],
            },
            {
                "eyebrow": "Por qué nosotros",
                "titulo": "El diferencial",
                "bajada": "Lo que nos hace distintos.",
                "fondo": "alt",
                "tarjetas": [
                    ("Tasa real, no estimada",
                     "Sistema conectado en tiempo real con los organismos que importan, "
                     "así que la tasa que te damos es la real, no una estimación."),
                    ("100% digital",
                     "Cargás, confirmás y cobrás sin pisar una sucursal."),
                    ("Línea de descuento permanente",
                     "Si preferís una línea permanente en vez de operación por operación, "
                     "tu comercial te arma una propuesta a medida."),
                ],
            },
        ],

        "publico": {
            "eyebrow": "A quién le sirve",
            "titulo": "Para quién",
            "bajada": "Comercios y empresas que cobran con cheques.",
            "texto": "Comercios y empresas que cobran con cheques y necesitan liquidez ya, "
                     "sin esperar el vencimiento.",
        },

        # Las capturas ya traen el marco del teléfono, así que se muestran
        # tal cual, una al lado de la otra.
        "app": {
            "titulo": "App Sur Finanzas",
            "bajada": "Así se ve en la app.",
            "imagenes": [
                {"src": "assets/servicios/app-cheques-1.jpg",
                 "ancho": 336, "alto": 652,
                 "alt": "Pantalla de la App Sur Finanzas para sacarle una foto al cheque"},
                {"src": "assets/servicios/app-cheques-2.jpg",
                 "ancho": 351, "alto": 657,
                 "alt": "Pantalla de la App Sur Finanzas con los datos del cheque leídos "
                        "y el descuento estimado"},
            ],
        },

        # Cuando esté el video, cargar "archivo" (y opcionalmente "poster").
        "video": {
            "titulo": "Video",
            "bajada": "Mirá el paso a paso en video.",
            "estado": "Video en producción",
            "archivo": "",
        },
        "cta": "Descontá tu cheque",
        "wa": "Hola Sur Finanzas, quiero descontar un cheque.",
    },
    {
        "archivo": "medios-de-pago.html",
        "nombre": "Medios de Pago & Cobranzas",
        "nombre_corto": "Medios de pago",
        "icono": "pagos",
        "imagen": "",
        "imagen_alt": "",
        "titulo": "Optimizá cómo cobra tu negocio",
        "gancho": "Cobranzas integrales.",
        "resumen": "Soluciones de cobro para optimizar la facturación de tu negocio o comercio.",
        "descripcion": "Soluciones integrales de cobro para optimizar la facturación y "
                       "los ingresos de tu negocio o comercio.",
        # PROVISORIO: los tres puntos son una relectura de la descripción, no
        # información propia del servicio. Reemplazar cuando llegue el detalle.
        "puntos": [
            ("Distintos medios de pago",
             "Un mismo circuito para las formas de cobro que usa tu comercio."),
            ("Facturación ordenada",
             "Los cobros quedan registrados y son fáciles de conciliar."),
            ("Mejores ingresos",
             "El objetivo es que entre más y entre mejor."),
        ],
        "cta": "Consultá por medios de pago",
        "wa": "Hola Sur Finanzas, quiero información sobre medios de pago y cobranzas.",
    },
    {
        "archivo": "compra-y-venta-de-oro.html",
        "nombre": "Compra y venta de oro",
        "icono": "oro",
        "imagen": "",
        "imagen_alt": "Lingotes y monedas de oro con iluminación cálida sobre fondo oscuro",
        "titulo": "Oro: un valor que se puede tocar",
        "gancho": "Tasación en el acto, pago inmediato.",
        "resumen": "Compra y venta de oro físico: lingotes, monedas y oro usado.",
        "descripcion": "Compra y venta de oro físico — la reserva de valor que no vive "
                       "en una pantalla ni depende de nadie más.",
        "foto_titulo": "Foto: lingotes y monedas de oro",
        "puntos": [],
        "orden": ["secciones", "publico", "ubicacion"],

        "secciones": [
            {
                "eyebrow": "Cómo opera",
                "titulo": "Cómo funciona",
                "bajada": "Operación en el día.",
                "texto": "Comprás o vendés oro físico en nuestra sucursal de Plaza Canning. "
                         "La cotización se actualiza según el valor internacional del oro y "
                         "te la confirmamos en el momento de la operación. Entrás con tu oro "
                         "o tu dinero, salís con la operación cerrada.",
                "tarjetas": [
                    ("Cotización en tiempo real",
                     "El precio del oro se actualiza según el valor internacional. Te "
                     "confirmamos la cotización exacta en el momento de la operación, sin "
                     "valores de referencia desactualizados."),
                ],
            },
            {
                "eyebrow": "Qué operamos",
                "titulo": "Qué podés operar",
                "bajada": "Tres formas de operar con oro físico.",
                "fondo": "alt",
                "tarjetas": [
                    ("Lingotes de oro certificados",
                     "Con certificado de pureza y peso verificado."),
                    ("Monedas de oro de inversión",
                     "Las más operadas del mercado internacional."),
                    ("Compra de oro usado",
                     "Joyas y piezas, sujeto a evaluación de pureza en el momento."),
                ],
            },
            {
                "eyebrow": "Por qué nosotros",
                "titulo": "Por qué en Sur Finanzas",
                "bajada": "No es un local de compraventa.",
                "tarjetas": [
                    ("Estándar de caudales",
                     "Custodia y manejo con el mismo estándar de seguridad que usamos en "
                     "el transporte de caudales."),
                    ("Atención personalizada",
                     "Te atiende un comercial, sin intermediarios."),
                    ("Respaldo de un holding",
                     "Trayectoria en gestión de valores, no un local de compraventa aislado."),
                ],
            },
        ],

        "publico": {
            "eyebrow": "A quién le sirve",
            "titulo": "Para quién",
            "bajada": "Quienes buscan resguardar valor fuera del sistema.",
            "texto": "Quienes buscan resguardar valor fuera del sistema financiero "
                     "tradicional, diversificar patrimonio, o necesitan liquidez rápida "
                     "a cambio de oro físico.",
        },

        # Los datos de la sucursal viven en empresa.py. Acá solo el CTA propio.
        "ubicacion": {
            "eyebrow": "La sucursal",
            "cta": "Consultá la cotización de hoy",
        },

        "cta": "Consultá la cotización de hoy",
        "wa": "Hola Sur Finanzas, quiero consultar la cotización del oro de hoy.",
    },
    {
        "archivo": "cajas-seguridad.html",
        "nombre": "Cajas de seguridad",
        "icono": "cajas",
        "imagen": "",
        "imagen_alt": "",
        "titulo": "Lo irremplazable, en el lugar más seguro",
        "gancho": "Acceso privado y confidencial.",
        "resumen": "Alquiler de módulos blindados para resguardar documentación y valores.",
        "descripcion": "Alquiler de módulos blindados bajo normas de alta seguridad. "
                       "Acceso privado y confidencial para el resguardo de documentación y valores.",
        "puntos": [],
        "orden": ["secciones", "publico"],

        "secciones": [
            {
                "eyebrow": "Cómo opera",
                "titulo": "Cómo funciona",
                "bajada": "Vos tenés la única llave.",
                "texto": "Alquilás una caja de seguridad del tamaño que necesites, con "
                         "contrato simple y renovación automática. Accedés en horario "
                         "extendido, con verificación de identidad en cada ingreso. Vos "
                         "tenés la única llave — ni el personal de Sur puede abrir tu caja "
                         "sin tu presencia.",
                "tarjetas": [
                    ("Acceso simple",
                     "Contrato simple, renovación automática y horario extendido para que "
                     "entres cuando lo necesites. Verificación de identidad en cada ingreso."),
                ],
            },
            {
                "eyebrow": "Opciones",
                "titulo": "Tamaños disponibles",
                "bajada": "Tres tamaños, según lo que necesites resguardar.",
                "fondo": "alt",
                "tarjetas": [
                    ("Chica", "Documentos, alhajas, objetos pequeños de valor."),
                    ("Mediana", "Contratos, colecciones, resguardo familiar."),
                    ("Grande", "Empresas o patrimonios que requieren mayor volumen."),
                ],
            },
            {
                "eyebrow": "Cómo la protegemos",
                "titulo": "Seguridad",
                "bajada": "El mismo estándar que el transporte de caudales.",
                "tarjetas": [
                    ("Bóveda blindada",
                     "Con el mismo estándar que el transporte de caudales."),
                    ("Acceso restringido",
                     "Acceso restringido y monitoreado, con registro de cada ingreso."),
                    ("Doble verificación",
                     "Verificación de identidad en cada ingreso, sin excepciones."),
                ],
            },
            {
                "eyebrow": "Extras",
                "titulo": "Más beneficios",
                "fondo": "alt",
                "tarjetas": [
                    ("Horario flexible",
                     "El mismo horario extendido del shopping. Nada de ir corriendo antes "
                     "de las 15."),
                    ("Acceso compartido con QR",
                     "¿Necesitás que alguien más entre a tu caja? Compartís un QR único con "
                     "hasta 2 o 3 personas de confianza — vos decidís con quién."),
                ],
            },
        ],

        "publico": {
            "eyebrow": "A quién le sirve",
            "titulo": "Para quién",
            "bajada": "Personas y empresas que necesitan resguardar.",
            "texto": "Personas y empresas que necesitan resguardar documentación, joyas, "
                     "contratos u objetos de valor fuera de su casa u oficina.",
        },
        "cta": "Reservá tu caja",
        "wa": "Hola Sur Finanzas, quiero reservar una caja de seguridad.",
    },
    {
        "archivo": "transporte-de-caudales.html",
        "nombre": "Transporte de caudales",
        "icono": "caudales",
        "imagen": "assets/servicios/transporte-de-caudales.jpg",
        "imagen_alt": "Camión blindado de Sur Finanzas estacionado en la calle",
        "titulo": "Que tu efectivo nunca sea tu problema",
        "gancho": "Unidades blindadas con seguimiento satelital.",
        "resumen": "Traslado y custodia de efectivo y activos, con cobertura asegurada.",
        "descripcion": "Traslado y custodia de dinero en efectivo y activos mediante unidades "
                       "blindadas, con seguimiento satelital y cobertura asegurada.",
        # Esta página no usa la grilla genérica de "En detalle": la información
        # va en los dos bloques de abajo, con foto al costado.
        "puntos": [],
        "orden": ["video", "bloques"],

        # Cuando esté el video, cargar "archivo" (y opcionalmente "poster").
        "video": {
            "titulo": "Así trabajamos",
            "bajada": "Mirá cómo operamos, en video.",
            "estado": "Video en producción",
            "archivo": "",
        },
        "bloques": [
            {
                "layout": "imagen-izquierda",
                "titulo": "Transporte y manejo de caudales",
                "descripcion": "Para empresas y comercios que mueven efectivo y "
                               "necesitan hacerlo con seguridad real.",
                "items": [
                    "Transporte terrestre en unidades blindadas",
                    "Seguimiento satelital durante todo el recorrido",
                    "Recuento y clasificación de valores",
                    "Atesoramiento y custodia",
                    "Armado de remesas para sucursales o puntos de venta",
                    "Cobertura asegurada de la operación",
                ],
                "cta": "Cotizá tu servicio de caudales",
                "wa": "Hola Sur Finanzas, quiero cotizar un servicio de transporte de caudales.",
                "imagen": "",
                "imagen_alt": "",
                "foto_titulo": "Foto del camión de caudales",
            },
            {
                "layout": "imagen-derecha",
                "fondo": "alt",
                "titulo": "Custodia de mercadería en tránsito",
                "descripcion": "Acompañamos tu carga hasta destino, con guardias armados "
                               "y protocolos que ya usan las grandes operaciones logísticas.",
                "para_quien": "Empresas que mueven mercadería de alto valor entre depósitos, "
                              "sucursales o rutas.",
                "pasos": [
                    ("Coordinamos la operación",
                     "Planificamos todo con tu equipo logístico antes de salir."),
                    ("Asignamos custodia armada",
                     "Guardias armados al vehículo durante todo el recorrido."),
                    ("Acompañamos hasta destino",
                     "La carga llega a destino, con protocolo verificado."),
                ],
                "cta": "Cotizá tu servicio de custodia",
                "wa": "Hola Sur Finanzas, quiero cotizar un servicio de custodia de mercadería.",
                "imagen": "",
                "imagen_alt": "",
                "foto_titulo": "Foto del camión de carga",
            },
        ],
        "cta": "Cotizá tu servicio",
        "wa": "Hola Sur Finanzas, quiero cotizar un servicio de transporte de caudales.",
    },
]


def corto(servicio):
    """Nombre acotado para chips y listados angostos."""
    return servicio.get("nombre_corto", servicio["nombre"])


# Formato (ruta, nombre) que usan plantilla.py y el generador del blog.
def pares():
    return [(f"servicios/{s['archivo']}", s["nombre"]) for s in SERVICIOS]
