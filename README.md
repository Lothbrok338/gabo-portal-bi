# GABO PORTAL BI — MVP 0.1

Portal de **Soluciones Empresariales Gabo**, independiente de cualquier proyecto institucional. Alojamiento pendiente; no contiene datos empresariales reales.

## ¿Qué está implementado?

- Proyecto Django 5.2 LTS con autenticación y sesiones reales.
- Empresas, usuarios miembros, informes, asignaciones de visibilidad por informe.
- Solo usuarios con membresía **y permiso explícito** pueden abrir un informe; superusuario administra desde Django Admin.
- Dashboard Dark Aurora adaptado, con modo demostración para informes sin URL.
- Incrustación de enlaces `https://app.powerbi.com/view?r=...` validados.
- Datos totalmente ficticios para el laboratorio, pruebas de autorizaciones y aislamiento entre empresas.
- Configuración preparada para PostgreSQL, Railway y GitHub Actions, **sin despliegue**.

**Alcance y seguridad:** `Publish to web` hace público el contenido en Microsoft. Nuestro login y permisos solo controlan el acceso al **portal**, no protegen el informe original. No insertar datos privados ni datos institucionales en este modo.

## Arranque local

Requiere Python 3.11+ y acceso a instalar dependencias:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
# Copiar .env.example a .env y configurar variables; Django no lee .env automáticamente:
# Windows PowerShell: $env:DEBUG="1"; $env:DJANGO_SECRET_KEY="clave-de-desarrollo-aleatoria"
# Linux/macOS: export DEBUG=1 DJANGO_SECRET_KEY="clave-de-desarrollo-aleatoria"
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ y entrar con las credenciales que imprimió `seed_demo`. Solo el superusuario tiene acceso a `/admin/`.

> En desarrollo se genera una clave provisional si falta `DJANGO_SECRET_KEY`. En producción es obligatorio proporcionar una clave larga y secreta mediante variables de entorno.

## Estructura

- `portal/` configuración de Django.
- `core/` entidades empresariales, comprobación de permisos, datos ficticios y pruebas.
- `templates/` interfaz Dark Aurora de inicio de sesión, biblioteca y visor.
- `static/` diseño visual.
- `design/referencia_dark_aurora.html` prototipo anterior **independiente**, solo referencia visual.
- `docs/ARQUITECTURA.md` decisiones, límites, seguridad y próximos hitos.
- `.github/workflows/ci.yml` pruebas automáticas al publicar en GitHub.

## Para cargar un informe público

Entrar al administrador `/admin/` con el superusuario, crear una empresa, asignar la membresía, agregar un dashboard con su URL de Publish to web y crear la concesión de acceso (`Dashboard grant`) para cada persona. Debe publicarse **solo contenido público o ficticio**. Sin URL, se muestra maqueta local.

## Producción (todavía no autorizada)

Configurar `DEBUG=0`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` (PostgreSQL) y `CSRF_TRUSTED_ORIGINS`. Ejecutar `python manage.py migrate` en un job controlado y servir con `gunicorn portal.wsgi:application --bind 0.0.0.0:$PORT`. Revisar cookies, TLS, respaldos, registros, controles antifuerza-bruta y aislamiento multicliente antes de publicar.

**No conectar un webhook de despliegue, crear servicios de Railway, modificar repositorios ajenos ni subir información institucional sin aprobación.**