#!/usr/bin/env python3
"""
Panel de administración del blog de Sur Finanzas.

El sitio público sigue siendo estático: este panel solo escribe los .md
en blog/_posts/ y dispara tools/generar-blog.py para rehacer el HTML.

Para probarlo en tu máquina:
    pip install -r admin/requirements.txt
    python3 admin/usuarios.py agregar nacho
    SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))") \
        python3 admin/app.py

En el VPS va detrás de gunicorn + nginx. Ver admin/README.md.
"""

import os
import datetime

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, abort, g)

import contenido as C
import seguridad as S
import formulario as F

BASE = os.path.dirname(os.path.abspath(__file__))


def cargar_env():
    """Lee admin/.env si existe. Lo que ya esté en el entorno tiene prioridad,
    así systemd (que usa EnvironmentFile) manda sobre el archivo."""
    ruta = os.path.join(BASE, ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


cargar_env()

app = Flask(__name__, template_folder=os.path.join(BASE, "templates"),
            static_folder=os.path.join(BASE, "static"))

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # En producción siempre por HTTPS. Poné ADMIN_INSEGURO=1 solo para probar en local.
    SESSION_COOKIE_SECURE=os.environ.get("ADMIN_INSEGURO") != "1",
    SESSION_COOKIE_NAME="sf_admin",
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(hours=8),
    MAX_CONTENT_LENGTH=C.MAX_IMAGEN_BYTES + 1024 * 1024,
    TEMPLATES_AUTO_RELOAD=False,
)

if not os.environ.get("SECRET_KEY"):
    app.logger.warning(
        "SECRET_KEY no está definida: se usa una aleatoria y las sesiones "
        "se pierden en cada reinicio. Definila en producción.")

URL_SITIO = os.environ.get("URL_SITIO", "https://www.surfinanzas.com.ar")


app.register_blueprint(F.bp)


@app.after_request
def cabeceras(respuesta):
    return S.aplicar_cabeceras(respuesta)


@app.template_filter("nombre_archivo")
def nombre_archivo(ruta):
    return (ruta or "").rsplit("/", 1)[-1]


@app.context_processor
def globales():
    return {
        "csrf_token": S.token_csrf,
        "usuario": session.get("usuario"),
        "nombre_usuario": session.get("nombre"),
        "url_sitio": URL_SITIO.rstrip("/"),
    }


# ---------------------------------------------------------------------------
# Sesión
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if S.usuario_actual():
        return redirect(url_for("lista"))

    espera = S.bloqueado()
    if request.method == "POST":
        if espera:
            flash(f"Demasiados intentos fallidos. Probá de nuevo en {espera // 60 + 1} minutos.", "error")
            return render_template("login.html", espera=espera), 429

        usuario = (request.form.get("usuario") or "").strip().lower()
        datos = S.verificar(usuario, request.form.get("password"))
        if not datos:
            S.registrar_fallo()
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("login.html", espera=0), 401

        S.limpiar_fallos()
        S.iniciar_sesion(usuario, datos)
        siguiente = request.args.get("siguiente", "")
        # Solo se acepta una ruta interna, nunca una URL a otro dominio
        if siguiente.startswith("/") and not siguiente.startswith("//"):
            return redirect(siguiente)
        return redirect(url_for("lista"))

    return render_template("login.html", espera=espera)


@app.route("/logout", methods=["POST"])
@S.login_requerido
def logout():
    S.validar_csrf()
    S.cerrar_sesion()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Listado
# ---------------------------------------------------------------------------

@app.route("/")
@S.login_requerido
def lista():
    notas = C.listar()
    return render_template(
        "lista.html",
        notas=notas,
        publicadas=sum(1 for n in notas if not n["borrador"]),
        borradores=sum(1 for n in notas if n["borrador"]),
    )


# ---------------------------------------------------------------------------
# Editor
# ---------------------------------------------------------------------------

@app.route("/nota/nueva")
@S.login_requerido
def nueva():
    nota = {
        "archivo": "", "slug": "", "titulo": "", "resumen": "",
        "fecha": datetime.date.today(), "categoria": "",
        "autor": g.nombre, "imagen": "", "destacado": False,
        "borrador": True, "cuerpo": "", "palabras": 0,
    }
    return render_template("editor.html", nota=nota, categorias=C.categorias(),
                           imagenes=C.listar_imagenes(), es_nueva=True)


@app.route("/nota/<archivo>")
@S.login_requerido
def editar(archivo):
    try:
        nota = C.leer(archivo)
    except C.ErrorContenido as err:
        flash(str(err), "error")
        return redirect(url_for("lista"))
    return render_template("editor.html", nota=nota, categorias=C.categorias(),
                           imagenes=C.listar_imagenes(), es_nueva=False)


@app.route("/nota/guardar", methods=["POST"])
@S.login_requerido
def guardar():
    S.validar_csrf()
    original = request.form.get("archivo_original") or None
    publicar = request.form.get("accion") == "publicar"

    datos = {
        "titulo": request.form.get("titulo"),
        "resumen": request.form.get("resumen"),
        "fecha": request.form.get("fecha"),
        "categoria": request.form.get("categoria"),
        "autor": request.form.get("autor"),
        "imagen": request.form.get("imagen"),
        "slug": request.form.get("slug"),
        "destacado": request.form.get("destacado") == "on",
        "borrador": not publicar,
        "cuerpo": request.form.get("cuerpo"),
    }

    try:
        archivo = C.guardar(datos, archivo_original=original)
    except C.ErrorContenido as err:
        flash(str(err), "error")
        nota = dict(datos, archivo=original or "", palabras=0)
        try:
            nota["fecha"] = datetime.date.fromisoformat(datos["fecha"])
        except (ValueError, TypeError):
            nota["fecha"] = datetime.date.today()
        return render_template("editor.html", nota=nota, categorias=C.categorias(),
                               imagenes=C.listar_imagenes(),
                               es_nueva=not original), 400

    ok, salida = C.generar()
    if not ok:
        flash("La nota se guardó, pero falló la regeneración del sitio: " + salida, "error")
    elif publicar:
        flash("Nota publicada. Ya está en vivo en el sitio.", "ok")
    else:
        flash("Borrador guardado. No se publica hasta que le des a Publicar.", "ok")

    return redirect(url_for("editar", archivo=archivo))


@app.route("/nota/eliminar", methods=["POST"])
@S.login_requerido
def eliminar():
    S.validar_csrf()
    try:
        C.eliminar(request.form.get("archivo", ""))
    except C.ErrorContenido as err:
        flash(str(err), "error")
        return redirect(url_for("lista"))

    ok, salida = C.generar()
    flash("Nota eliminada." if ok else "Nota eliminada, pero falló la regeneración: " + salida,
          "ok" if ok else "error")
    return redirect(url_for("lista"))


# ---------------------------------------------------------------------------
# Acciones auxiliares
# ---------------------------------------------------------------------------

@app.route("/regenerar", methods=["POST"])
@S.login_requerido
def regenerar():
    S.validar_csrf()
    ok, salida = C.regenerar_todo()
    flash("Sitio regenerado (servicios y blog)." if ok
          else "Falló la regeneración: " + salida, "ok" if ok else "error")
    return redirect(request.referrer or url_for("lista"))


@app.route("/api/preview", methods=["POST"])
@S.login_requerido
def preview():
    S.validar_csrf()
    texto = (request.get_json(silent=True) or {}).get("cuerpo", "")
    if len(texto) > 200_000:
        return jsonify({"error": "El texto es demasiado largo."}), 413
    return jsonify({"html": C.render_markdown(texto)})


@app.route("/api/imagen", methods=["POST"])
@S.login_requerido
def subir_imagen():
    S.validar_csrf()
    archivo = request.files.get("imagen")
    if not archivo:
        return jsonify({"error": "No llegó ningún archivo."}), 400
    try:
        ruta, (w, h) = C.guardar_imagen(archivo)
    except C.ErrorContenido as err:
        return jsonify({"error": str(err)}), 400
    return jsonify({"ruta": ruta, "ancho": w, "alto": h})


@app.route("/mensajes")
@S.login_requerido
def mensajes():
    todos = F.leer_mensajes()
    area = request.args.get("area", "")
    filtrados = [m for m in todos if not area or m.get("area") == area]
    return render_template(
        "mensajes.html",
        mensajes=filtrados,
        total=len(todos),
        areas=sorted({m.get("area", "") for m in todos if m.get("area")}),
        area_activa=area,
        smtp_ok=bool(F._config_smtp()),
    )


@app.route("/simulador", methods=["GET", "POST"])
@app.route("/simulador/<archivo>", methods=["GET", "POST"])
@S.login_requerido
def simulador(archivo=None):
    disponibles = C.servicios_con_simulador()
    if not disponibles:
        flash("Ningún servicio tiene simulador configurado.", "error")
        return redirect(url_for("lista"))

    archivo = archivo or disponibles[0]["archivo"]
    try:
        servicio, config = C.leer_simulador(archivo)
    except C.ErrorContenido as err:
        flash(str(err), "error")
        return redirect(url_for("lista"))

    if request.method == "POST":
        S.validar_csrf()
        try:
            config = C.guardar_simulador(archivo, request.form)
        except C.ErrorContenido as err:
            flash(str(err), "error")
            # Se le devuelven los valores que cargó, para que no pierda lo escrito
            return render_template("simulador.html", servicio=servicio,
                                   config=_config_del_form(request.form, config),
                                   disponibles=disponibles, archivo=archivo,
                                   ejemplos=[]), 400

        ok, salida = C.regenerar_todo()
        if ok:
            flash("Simulador actualizado. Los nuevos valores ya están en el sitio.", "ok")
        else:
            flash("Se guardó la configuración, pero falló la regeneración: " + salida, "error")
        return redirect(url_for("simulador", archivo=archivo))

    return render_template("simulador.html", servicio=servicio, config=config,
                           disponibles=disponibles, archivo=archivo,
                           ejemplos=_ejemplos(config))


def _config_del_form(form, anterior):
    """Rearma la config con lo que el usuario escribió, para repintar el form."""
    salida = dict(anterior)
    for campo in ("minimo", "maximo", "paso", "inicial", "plazo_inicial"):
        if form.get(campo):
            salida[campo] = form.get(campo)
    if form.get("tasa_mensual"):
        salida["tasa_texto"] = form.get("tasa_mensual")
    if form.get("plazos"):
        salida["plazos_texto"] = form.get("plazos")
    return salida


def _ejemplos(config):
    """Tabla chica de cuotas, para ver el efecto de la tasa de un vistazo."""
    tasa = config["tasa_mensual"]
    montos = [config["minimo"], config["inicial"], config["maximo"]]
    plazos = config["plazos"][:4]
    filas = []
    for m in sorted(set(montos)):
        celdas = []
        for p in plazos:
            c = C.cuota(m, tasa, p)
            celdas.append({"plazo": p, "cuota": round(c), "total": round(c * p)})
        filas.append({"monto": m, "celdas": celdas})
    return {"plazos": plazos, "filas": filas}


@app.route("/media/<path:nombre>")
@S.login_requerido
def media(nombre):
    """Sirve las imágenes de assets/blog/ para las vistas previas del panel."""
    from flask import send_from_directory
    if "/" in nombre or "\\" in nombre or nombre.startswith("."):
        abort(404)
    if not nombre.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        abort(404)
    if not os.path.exists(os.path.join(C.IMG_DIR, nombre)):
        abort(404)
    return send_from_directory(C.IMG_DIR, nombre, max_age=0)


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(413)
@app.errorhandler(429)
def error_cliente(err):
    return render_template("error.html", codigo=err.code,
                           mensaje=getattr(err, "description", "")), err.code


@app.errorhandler(500)
def error_servidor(err):
    app.logger.exception("Error interno")
    return render_template("error.html", codigo=500,
                           mensaje="Se rompió algo del lado del servidor."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PUERTO", 8001)), debug=False)
