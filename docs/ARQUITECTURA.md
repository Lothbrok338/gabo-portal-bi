# Arquitectura y alcance — GABO PORTAL BI v0.1

## Propósito
Producto comercial independiente de Soluciones Empresariales Gabo, NO es OpenBI ni pertenece a proyectos institucionales. No se copian PBIX ni fuentes de trabajo y tampoco se alojan datos internos.

## Flujo

Usuario → HTTPS → Django (login, sesión y comprobación de permisos) → catálogo filtrado por empresa / concesión → iframe de Publish to web **solo cuando el admin vincula un informe público** → Power BI sirve los datos directamente al navegador.

## Decisiones

1. **Una sola aplicación Django** para minimizar piezas y gasto operativo. Django Admin inicialmente **solo para superusuarios**. Roles «gestor» y «lector» están modelados, pero sus pantallas de gestión delegada quedan pendientes. No afirmar que el gestor ya puede administrar usuarios.
2. **SQLite para pruebas y PostgreSQL para producción**; `DATABASE_URL` permite cambiar la base sin modificar lógica.
3. **Permisos de biblioteca**: empresa activa + membresía del usuario + asignación explícita al informe. Un cliente no ve el catálogo de otro. Django superuser puede administrar todos.
4. **Nunca confundir este control con protección del informe original**: Publish to web implica URL e información públicas. Un iframe no oculta realmente el enlace.
5. **Tema Dark Aurora**: replica visualmente la referencia sin depender de imágenes externas.
6. **Sin desplegar**: GitHub/CI se utilizan para versionado y validación; Railway y Cloudflare después, con aprobación.

## Seguridad: antes de clientes reales

- Almacenar secretos únicamente en variables de entorno y revisar políticas CORS/CSP, HTTP TLS, alertas, respaldos y recuperación.
- Django protege contraseñas, sesiones y CSRF mediante componentes nativos. Para producción añadir limitación de intentos de login, controles de auditoría, MFA para administradores y políticas de retención.
- El usuario final **puede extraer el enlace público del iframe**. No confiar en enlaces cifrados del lado navegador ni URL no adivinable como protección de información financiera.
- No hay RLS de Power BI aplicado por permisos del portal. Si se necesitan informes confidenciales, migrar a Embedded con capacidad y tokens privados, o solución propia con autorización de datos.
- No habilitar automáticamente `is_staff` a gestores empresariales. El admin de Django debe mantenerse restringido hasta desarrollar administración segregada por empresa.
- Las comprobaciones de este repositorio no reemplazan auditoría de seguridad ni pruebas de despliegue.

## Pruebas incluidas

`python manage.py test`: aislamiento entre empresas, membresía sin asignación, superusuario, dashboard desactivado, validación de URLs y control de logout.

## Próximos hitos

1. Ejecutar y validar los tests con dependencias instaladas.
2. Aprobar la estética Dark Aurora.
3. Vincular dos dashboards **ficticios** publicados desde una cuenta comercial independiente.
4. Crear administración visual de usuarios y permisos por empresa (sin acceso global a otros tenants).
5. Agregar tests de uso real (navegador, mobile, CSRF, reverse proxy y seguridad).
6. Autorizar infraestructura Railway/Cloudflare, configurar PostgreSQL, backups, monitoreo y despliegue.
7. Medir costo por cliente/mes y soporte antes de comercialización.

## Iteración 0.2 — gestión empresarial (laboratorio)

- `/portal/gestion/` lista únicamente las empresas administrables por el usuario.
- Cada gestor puede crear y editar informes solo de su empresa y elegir qué miembros tienen acceso desde el portal; los lectores no acceden a estas pantallas.
- Ningún formulario acepta un identificador de empresa arbitrario desde el navegador. Toda ruta comprueba pertenencia y rol del gestor; recurso ajeno recibe 404.
- Las asignaciones se validan contra la membresía activa de la empresa; edición y revocación son transaccionales.
- **Pendiente de la siguiente iteración:** alta/baja de usuarios, auditoría persistente de cambios de permisos, MFA, controles de abuso y revisión de seguridad para producción.