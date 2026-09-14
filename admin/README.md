# Panel del blog — instalación y uso

## Cómo funciona

El sitio público **sigue siendo estático**. El panel no lo sirve: solo escribe
archivos y dispara el generador.

```
Panel (Flask, con login)
   │
   ├─ escribe  blog/_posts/2026-09-01-mi-nota.md
   ├─ guarda   assets/blog/mi-imagen.jpg
   │
   └─ ejecuta  tools/generar-blog.py
                   │
                   └─ escribe  blog/mi-nota.html
                               blog/index.html
                               sitemap.xml
                                    │
                                    └─ nginx los sirve como archivos estáticos
```

Consecuencias prácticas:

- Si el panel se cae, **el sitio sigue funcionando**. Solo no se pueden cargar notas.
- No hay base de datos. El backup es copiar `blog/_posts/` y `assets/blog/`.
- Las páginas públicas no ejecutan nada del lado del servidor.

---

## Probarlo en tu máquina

```bash
cd /home/nacho/surfinanzas
python3 -m venv .venv
source .venv/bin/activate
pip install -r admin/requirements.txt

python3 admin/usuarios.py agregar nacho          # te pide la contraseña

SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))") \
ADMIN_INSEGURO=1 URL_SITIO=http://localhost:8080 \
python3 admin/app.py
```

Abrí <http://127.0.0.1:8001>.

`ADMIN_INSEGURO=1` permite la cookie de sesión sin HTTPS. **Solo para local:
en el VPS nunca.**

Para ver el sitio público al mismo tiempo, en otra terminal:

```bash
cd /home/nacho/surfinanzas && python3 -m http.server 8080
```

---

## Instalación en el VPS

Asumo Ubuntu/Debian con nginx. Ajustá rutas y dominios según tu caso.

### 1. Subir el proyecto

```bash
sudo mkdir -p /var/www/surfinanzas
sudo chown -R $USER:$USER /var/www/surfinanzas
rsync -av --delete \
      --exclude '.venv' --exclude '__pycache__' \
      --exclude 'admin/.env' --exclude 'admin/usuarios.json' \
      --exclude '*:Zone.Identifier' --exclude 'deploy-*.zip' \
      ./ usuario@tu-vps:/var/www/surfinanzas/
```

### 2. Entorno de Python

```bash
cd /var/www/surfinanzas
python3 -m venv .venv
.venv/bin/pip install -r admin/requirements.txt
```

### 3. Configuración

```bash
cp admin/.env.ejemplo admin/.env
nano admin/.env          # poné SECRET_KEY y URL_SITIO
chmod 600 admin/.env
```

Generá la `SECRET_KEY` con:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Usuarios

```bash
.venv/bin/python admin/usuarios.py agregar nacho
.venv/bin/python admin/usuarios.py agregar marketing
.venv/bin/python admin/usuarios.py listar
```

Mínimo 12 caracteres. No hay registro público ni recuperación por email:
si alguien pierde la clave, se la reseteás con `usuarios.py password <usuario>`.

### 5. Permisos

El servicio corre como `www-data` y necesita escribir en tres lugares:

```bash
sudo chown -R www-data:www-data /var/www/surfinanzas/blog \
                                /var/www/surfinanzas/assets/blog \
                                /var/www/surfinanzas/admin
sudo chown www-data:www-data /var/www/surfinanzas/sitemap.xml
sudo chmod 600 /var/www/surfinanzas/admin/.env \
               /var/www/surfinanzas/admin/usuarios.json
```

### 6. Servicio

```bash
sudo cp admin/despliegue/surfinanzas-admin.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now surfinanzas-admin
sudo systemctl status surfinanzas-admin
```

Si `Type=notify` te da problemas con tu versión de gunicorn, cambialo a
`Type=simple` en el archivo del servicio.

### 7. nginx + certificado

```bash
sudo cp admin/despliegue/nginx.conf /etc/nginx/sites-available/surfinanzas
sudo ln -s /etc/nginx/sites-available/surfinanzas /etc/nginx/sites-enabled/
sudo nginx -t
sudo certbot --nginx -d surfinanzas.com.ar -d www.surfinanzas.com.ar -d panel.surfinanzas.com.ar
sudo systemctl reload nginx
```

Antes de esto, apuntá `panel.surfinanzas.com.ar` al VPS con un registro A.

---

## Seguridad

Lo que ya viene resuelto:

- Contraseñas hasheadas con **scrypt**, nunca en texto plano.
- Bloqueo de 15 minutos tras 5 intentos fallidos, por IP.
- Cookie de sesión `HttpOnly`, `Secure`, `SameSite=Lax`, expira a las 8 horas.
- **Token CSRF** en todos los formularios y llamadas al servidor.
- Las imágenes se validan por **contenido real** (con Pillow), no por extensión.
  Un `.php` renombrado a `.jpg` se rechaza.
- Toda ruta de archivo se valida contra escape de directorio (`../`).
- Cabeceras: CSP estricta, `X-Frame-Options: DENY`, `nosniff`, `no-store`.
- El panel manda `noindex` y no está linkeado desde ninguna página pública.
- systemd corre el servicio con `ProtectSystem=strict` y solo tres rutas escribibles.
- nginx bloquea `/admin/`, `/tools/`, `/blog/_posts/` y los `.md`/`.py` del sitio público.

Lo que depende de vos:

1. **HTTPS obligatorio.** Sin certificado, la cookie de sesión no viaja y no vas a poder entrar.
2. **`SECRET_KEY` propia y estable.** Si no la definís, se genera una al azar y
   todas las sesiones se cierran en cada reinicio.
3. **Restringí el panel por IP** si el equipo trabaja siempre desde el mismo lugar.
   Está comentado en `nginx.conf` y es la mejora de seguridad más barata que hay.
4. **Backup.** Un cron diario alcanza:
   ```bash
   0 3 * * * tar czf /root/backups/blog-$(date +\%F).tgz \
             /var/www/surfinanzas/blog/_posts /var/www/surfinanzas/assets/blog
   ```
5. **Mantené el sistema actualizado**, sobre todo Flask y Pillow.

Nota sobre el bloqueo por intentos: se guarda en memoria del proceso. Con dos
workers de gunicorn, en el peor caso se toleran ~10 intentos en vez de 5. Es
suficiente para frenar fuerza bruta. Si querés algo más estricto, poné
`fail2ban` sobre el log de nginx o bajá a un solo worker.

---

## Formulario de contacto

El mismo servicio expone `POST /api/contacto`, que nginx publica en el dominio
del sitio (no en el del panel) para que no haya CORS de por medio.

El orden de las operaciones es a propósito:

1. valida los datos,
2. **guarda** el mensaje en `datos/mensajes.jsonl`,
3. recién ahí intenta mandarlo por mail.

Si el SMTP falla, el mensaje ya está guardado y se lee desde *Mensajes* en el
panel. Un formulario que pierde consultas es peor que no tener formulario.

### Configurar el envío por mail

En `admin/.env`, con los datos del proveedor de correo de `surfinanzas.com.ar`:

```
SMTP_HOST=mail.tuproveedor.com
SMTP_PUERTO=587
SMTP_USUARIO=web@surfinanzas.com.ar
SMTP_PASSWORD=la-clave
SMTP_DESDE=web@surfinanzas.com.ar
SMTP_SEGURIDAD=starttls
```

`SMTP_SEGURIDAD` es `starttls` (puerto 587, lo más común), `ssl` (puerto 465)
o `ninguna`. Después: `sudo systemctl restart surfinanzas-admin`.

**Sin configurar nada el formulario ya funciona**: guarda los mensajes y se
ven en el panel. El aviso por mail lo sumás cuando tengas las credenciales.

### A dónde llega cada consulta

El campo *Área* del formulario decide el destinatario: Reclamos va a
`Reclamos@`, Legales a `Legales@`, y así. El mapa está en `AREAS`, arriba de
`admin/formulario.py`. El `Reply-To` es el mail del visitante, así que
respondés desde tu cliente de correo como si te hubiera escrito directo.

### Defensas

- **Honeypot**: un campo oculto que las personas no ven. Si viene completo, se
  descarta en silencio (al bot se le responde que salió todo bien).
- **Límite de 5 envíos por hora y por IP** en la aplicación, más
  `limit_req` en nginx (10 por minuto) que frena el tráfico antes de Python.
- **Sin inyección de cabeceras**: todo lo que va a un encabezado del mail se
  limpia de saltos de línea, así nadie puede colar un `Bcc:`.
- Los mensajes se guardan en `datos/`, que nginx tiene bloqueado, con permisos 600.

### Backup

Sumá `datos/` al backup: ahí viven consultas de personas reales.

```bash
0 3 * * * tar czf /root/backups/sur-$(date +\%F).tgz \
          /var/www/surfinanzas/blog/_posts \
          /var/www/surfinanzas/assets/blog \
          /var/www/surfinanzas/datos
```

---

## Simulador de cuotas

La tasa y el rango de montos del simulador de microcréditos se editan desde
el panel, en **Simulador**. Al guardar se regenera el sitio y el cambio queda
en vivo enseguida.

Cómo está armado:

- `tools/servicios.py` trae los **valores por defecto**. Si no configuraste
  nada, son los que se usan: un deploy nuevo funciona sin tocar el panel.
- El panel guarda lo suyo en `datos/simulador.json`, que **pisa** esos valores.
- Borrando ese archivo se vuelve al default del código.

Se validan la tasa (0% a 100% mensual), que el mínimo sea menor que el máximo,
que el monto inicial caiga dentro del rango, y que el plazo destacado sea uno
de los plazos cargados. Si algo no cierra, no se guarda nada.

La pantalla trae una vista previa que recalcula la cuota mientras escribís, y
una tabla con las cuotas de la configuración guardada, para ver el efecto de
la tasa de un vistazo.

**Ojo:** esa tasa la ve cualquiera que entre a la web. El aviso rojo de la
pantalla está para eso.

### Qué escribe el panel

Al regenerar toca estas rutas, y por eso están en `ReadWritePaths` del
servicio de systemd:

```
blog/  servicios/  assets/blog/  datos/  admin/
index.html  nosotros.html  sitemap.xml
```

Si movés el proyecto de lugar, actualizá esas rutas en
`admin/despliegue/surfinanzas-admin.service` (o volvé a correr el instalador,
que las ajusta solo).

---

## Uso diario

**Escribir una nota:** entrás al panel, *Nota nueva*, cargás título, resumen y
texto. *Guardar borrador* la deja invisible; *Publicar* la sube al sitio en el
acto.

**Formato:** la barra de arriba del editor pone negrita, subtítulos, listas,
citas, enlaces e imágenes. Por abajo es Markdown, así que también podés
escribirlo a mano. *Vista previa* muestra exactamente cómo va a quedar, porque
usa el mismo renderizador que el generador.

**Portada:** arrastrás una imagen sobre el recuadro o la elegís del disco. Se
redimensiona sola a 1600px y se convierte a JPG. Si no ponés ninguna, la nota
usa un fondo de marca con el isotipo.

**Bajar una nota del sitio:** abrila y dale *Guardar borrador*. El `.md` se
conserva, el `.html` desaparece del sitio y del índice.

**Eliminar:** va a `blog/_posts/_papelera/`, no se borra de verdad. Si te
arrepentís, la movés de vuelta y corrés *Regenerar sitio*.

**Regenerar sitio:** rehace todo el HTML a partir de los `.md`. Sirve si tocaste
algo a mano por SSH o si querés forzar una reconstrucción.

**Atajo:** `Ctrl+S` (o `Cmd+S`) guarda el borrador sin salir del editor.

---

## Si algo falla

```bash
sudo systemctl status surfinanzas-admin      # ¿está corriendo?
sudo journalctl -u surfinanzas-admin -n 50   # últimos errores
sudo nginx -t                                # ¿la config de nginx está bien?
```

**"Se guardó, pero falló la regeneración":** el `.md` está a salvo; lo que
falló fue el generador. Miralo a mano:

```bash
cd /var/www/surfinanzas && sudo -u www-data .venv/bin/python tools/generar-blog.py
```

**No puedo iniciar sesión y la contraseña es correcta:** casi siempre es la
cookie. Verificá que estás entrando por `https://` y que `ADMIN_INSEGURO` no
esté en `1`.

**Publiqué y no veo el cambio:** recargá con `Ctrl+Shift+R`. Si usás Cloudflare
por delante, purgá la caché.
