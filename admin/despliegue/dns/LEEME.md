# DNS de surfinanzas.com.ar

- `zona-anterior.txt` — la exportación de Cloudflare del 28/09/2026, como estaba.
- `zona-nueva.txt` — lo que hay que tener. Se importa en Cloudflare:
  **Websites → surfinanzas.com.ar → DNS → Records → Import and Export → Import**.

Importar **agrega** registros: no borra nada. Así que el orden es:
primero borrar los viejos, después importar.

## Qué se borra y por qué

| Registro | Por qué |
|---|---|
| `A surfinanzas.com.ar` y `A www` → 66.97.39.70 | Apuntan al sitio viejo. Los reemplaza el VPS. |
| `AAAA` del dominio y de `www` | Son direcciones IPv6 de Cloudflare. El VPS se usa por IPv4. |
| `A ftp`, `A mail`, `A mx1` → 200.58.x.x | Del hosting anterior. El correo hoy es Microsoft 365. |
| `CNAME webmail` → surfinanzas.com.ar | Llevaba al webmail viejo; hoy apuntaría al sitio nuevo. El correo se lee en Outlook. |
| `TXT mail._domainkey` | DKIM del hosting anterior. |
| `include:spf.hostmar.com` dentro del SPF | Del hosting anterior. Queda solo el de Microsoft. |
| `TXT _acme-challenge` (dos) | Restos de una validación de certificado ya terminada. |
| `TXT "11.08.2026"` y `TXT "06.08.2026"` | Sin ninguna función. |
| `A`/`AAAA` de `api` y `qa` | Del sitio viejo. Confirmado que no se usan. |
| `A autoconfig` | Con `autodiscover` de Microsoft 365 alcanza. |
| `CNAME k2._domainkey` y `k3._domainkey` | Mailchimp, que no se usa. |

## Confirmado con el cliente (28/09/2026)

- **`api` y `qa`**: quedaron del sitio viejo, no se usan. Se borran.
- **Mailchimp (`k2._domainkey` y `k3._domainkey`)**: no se usa Mailchimp.
  Se borran.
- **`spf.hostmar.com`**: sale del SPF, porque el correo es Microsoft 365. Si
  el formulario de la web termina enviando por otro proveedor, hay que sumar
  ese `include` al SPF.
- **`autoconfig`**: con `autodiscover` de Microsoft alcanza. Se borra.

## Nube gris, no naranja

Los registros del VPS van con el proxy de Cloudflare **apagado** (nube gris,
`cf-proxied:false`). Es lo que necesita certbot para emitir el certificado sin
vueltas. Una vez que el sitio esté andando con HTTPS, se puede encender el
proxy, pero antes hay que poner el modo SSL de Cloudflare en **Full (strict)**;
si se enciende en "Flexible", el sitio entra en un bucle de redirecciones.

El TTL quedó en 300 segundos (5 minutos) para poder corregir rápido durante la
instalación. Después conviene subirlo a 3600.
