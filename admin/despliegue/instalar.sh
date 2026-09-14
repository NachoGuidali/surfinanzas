#!/usr/bin/env bash
#
# Instalador del panel de Sur Finanzas en el VPS.
#
#   sudo bash admin/despliegue/instalar.sh
#
# Qué hace:
#   1. crea el entorno de Python e instala las dependencias
#   2. genera admin/.env con una SECRET_KEY nueva (si todavía no existe)
#   3. ajusta permisos para el usuario del servicio
#   4. instala y arranca el servicio de systemd
#
# Qué NO hace (queda para vos, porque depende de tu dominio):
#   - tocar la configuración de nginx
#   - pedir el certificado con certbot
#   - crear los usuarios del panel
#
# Es idempotente: podés correrlo de nuevo sin romper nada. Nunca pisa
# un .env ni un usuarios.json que ya existan.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICIO="surfinanzas-admin"
USUARIO_SERVICIO="${USUARIO_SERVICIO:-www-data}"
PUERTO="${PUERTO:-8001}"

verde()  { printf "\033[0;32m%s\033[0m\n" "$*"; }
amar()   { printf "\033[0;33m%s\033[0m\n" "$*"; }
rojo()   { printf "\033[0;31m%s\033[0m\n" "$*"; }
paso()   { printf "\n\033[1;36m▸ %s\033[0m\n" "$*"; }

# --- Comprobaciones previas ------------------------------------------------

if [[ $EUID -ne 0 ]]; then
  rojo "Este script necesita sudo (instala un servicio de systemd y ajusta permisos)."
  echo  "  sudo bash admin/despliegue/instalar.sh"
  exit 1
fi

for archivo in admin/app.py tools/generar-blog.py index.html; do
  if [[ ! -f "$RAIZ/$archivo" ]]; then
    rojo "No encuentro $archivo en $RAIZ."
    echo  "¿Estás corriendo el script desde la carpeta del proyecto?"
    exit 1
  fi
done

if ! id "$USUARIO_SERVICIO" &>/dev/null; then
  rojo "El usuario «$USUARIO_SERVICIO» no existe en este sistema."
  echo  "Pasale otro con:  USUARIO_SERVICIO=nginx sudo -E bash $0"
  exit 1
fi

verde "Proyecto:  $RAIZ"
verde "Servicio corre como:  $USUARIO_SERVICIO"
verde "Puerto interno:  $PUERTO"

# --- 1. Entorno de Python --------------------------------------------------

paso "Entorno de Python"

if ! command -v python3 &>/dev/null; then
  rojo "No hay python3 instalado."; exit 1
fi

if [[ ! -d "$RAIZ/.venv" ]]; then
  python3 -m venv "$RAIZ/.venv"
  echo "  entorno creado en .venv/"
else
  echo "  .venv ya existía, lo reuso"
fi

"$RAIZ/.venv/bin/pip" install --quiet --upgrade pip
"$RAIZ/.venv/bin/pip" install --quiet -r "$RAIZ/admin/requirements.txt"
echo "  dependencias instaladas:"
"$RAIZ/.venv/bin/pip" list 2>/dev/null | grep -iE '^(flask|markdown|pillow|gunicorn)' | sed 's/^/    /'

# --- 2. Configuración ------------------------------------------------------

paso "Configuración (admin/.env)"

if [[ -f "$RAIZ/admin/.env" ]]; then
  amar "  Ya existe admin/.env — no lo toco."
  amar "  Si querés regenerarlo, borralo y volvé a correr el script."
else
  read -rp "  Dominio público del sitio [https://www.surfinanzas.com.ar]: " URL_SITIO
  URL_SITIO="${URL_SITIO:-https://www.surfinanzas.com.ar}"

  CLAVE="$("$RAIZ/.venv/bin/python" -c 'import secrets; print(secrets.token_hex(32))')"
  cat > "$RAIZ/admin/.env" <<EOF
SECRET_KEY=$CLAVE
URL_SITIO=$URL_SITIO
PUERTO=$PUERTO
EOF
  verde "  admin/.env creado con una SECRET_KEY nueva"
fi

chmod 600 "$RAIZ/admin/.env"
chown "$USUARIO_SERVICIO":"$USUARIO_SERVICIO" "$RAIZ/admin/.env"

# --- 3. Permisos -----------------------------------------------------------

paso "Permisos de escritura"

# El panel solo necesita escribir en estos lugares. El resto queda de solo lectura.
for ruta in "$RAIZ/blog" "$RAIZ/servicios" "$RAIZ/assets/blog" "$RAIZ/admin" "$RAIZ/datos"; do
  mkdir -p "$ruta"
  chown -R "$USUARIO_SERVICIO":"$USUARIO_SERVICIO" "$ruta"
  echo "  escribible: ${ruta#"$RAIZ"/}"
done

# El panel también reescribe estos archivos sueltos al regenerar
for archivo in "$RAIZ/sitemap.xml" "$RAIZ/index.html" "$RAIZ/nosotros.html"; do
  touch "$archivo"
  chown "$USUARIO_SERVICIO":"$USUARIO_SERVICIO" "$archivo"
  echo "  escribible: ${archivo#"$RAIZ"/}"
done

[[ -f "$RAIZ/admin/usuarios.json" ]] && chmod 600 "$RAIZ/admin/usuarios.json"

# --- 4. Servicio de systemd ------------------------------------------------

paso "Servicio de systemd"

sed -e "s|/var/www/surfinanzas|$RAIZ|g" \
    -e "s|^User=.*|User=$USUARIO_SERVICIO|" \
    -e "s|^Group=.*|Group=$USUARIO_SERVICIO|" \
    -e "s|127.0.0.1:8001|127.0.0.1:$PUERTO|" \
    "$RAIZ/admin/despliegue/$SERVICIO.service" > "/etc/systemd/system/$SERVICIO.service"

systemctl daemon-reload
systemctl enable --quiet "$SERVICIO"
systemctl restart "$SERVICIO"
sleep 2

if systemctl is-active --quiet "$SERVICIO"; then
  verde "  El servicio está corriendo en 127.0.0.1:$PUERTO"
else
  rojo "  El servicio no arrancó. Mirá el detalle con:"
  echo  "    journalctl -u $SERVICIO -n 40 --no-pager"
  exit 1
fi

# --- Qué falta -------------------------------------------------------------

USUARIOS_EXISTEN=$([[ -f "$RAIZ/admin/usuarios.json" ]] && echo sí || echo no)

cat <<EOF

$(verde "Listo. Falta lo que depende de tu dominio:")

  1. Crear al menos un usuario  $([[ $USUARIOS_EXISTEN == no ]] && echo "← todavía no hay ninguno" || echo "(ya hay usuarios cargados)")

       sudo -u $USUARIO_SERVICIO $RAIZ/.venv/bin/python $RAIZ/admin/usuarios.py agregar nacho

  2. Apuntar panel.TU-DOMINIO al VPS con un registro A en tu DNS.

  3. Configurar nginx (editá dominios y rutas antes de copiarlo):

       sudo cp $RAIZ/admin/despliegue/nginx.conf /etc/nginx/sites-available/surfinanzas
       sudo nano /etc/nginx/sites-available/surfinanzas
       sudo ln -sf /etc/nginx/sites-available/surfinanzas /etc/nginx/sites-enabled/
       sudo nginx -t && sudo systemctl reload nginx

  4. Pedir el certificado (sin HTTPS el panel no deja iniciar sesión):

       sudo certbot --nginx -d TU-DOMINIO -d www.TU-DOMINIO -d panel.TU-DOMINIO

$(amar "Recomendado: limitá el panel a las IPs de tu equipo.")
  Está comentado en nginx.conf, en el bloque de panel. Es la mejora de
  seguridad más barata que hay.

Comandos útiles:
  systemctl status $SERVICIO
  journalctl -u $SERVICIO -f
EOF
