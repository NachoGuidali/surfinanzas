#!/usr/bin/env bash
# Actualiza el sitio en el servidor: baja los cambios y deja los permisos
# como los necesita el panel.
#
#   sudo bash admin/despliegue/actualizar.sh
#
# git pull corre con el usuario que lo ejecuta, así que los archivos nuevos
# quedan a su nombre. El panel corre como www-data y tiene que poder escribir
# en las carpetas que regenera: por eso el chown de abajo.

set -euo pipefail

RAIZ="${RAIZ:-/var/www/surfinanzas}"
USUARIO_SERVICIO="${USUARIO_SERVICIO:-www-data}"
cd "$RAIZ"

echo "→ Bajando cambios"
git pull --ff-only

echo "→ Permisos"
chown -R "$USUARIO_SERVICIO":"$USUARIO_SERVICIO" \
    blog servicios assets/blog datos admin
chown "$USUARIO_SERVICIO":"$USUARIO_SERVICIO" index.html nosotros.html sitemap.xml
chmod 600 admin/.env admin/usuarios.json

echo "→ Reiniciando el panel"
systemctl restart surfinanzas-admin
sleep 2
systemctl is-active --quiet surfinanzas-admin && echo "   panel activo" || {
    echo "   ✗ el panel no arrancó: journalctl -u surfinanzas-admin -n 30"; exit 1; }

codigo=$(curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/login || true)
echo "→ Panel responde $codigo (tiene que ser 200)"
echo "Listo."
