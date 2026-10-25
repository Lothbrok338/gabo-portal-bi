# Tareas siguientes para Codex

Este repositorio es exclusivo del negocio comercial Gabo Portal BI. Prohibido importar código o datos institucionales. No realizar despliegues sin permiso.

## Iteración 1 — completar base
- Instalar dependencias, ejecutar `python manage.py check`, `python manage.py makemigrations --check`, `python manage.py migrate` y `python manage.py test`.
- Revisar el control de accesos de `permitted_dashboards` y la consistencia entre `Membership` y `DashboardGrant`.
- Ejecutar `seed_demo` y comprobar 3 usuarios con permisos diferentes usando navegador real.
- Comparar visualmente la interfaz con `design/vista_previa.png`; ajustar responsividad.

## Iteración 2 — pantallas de administración
- Diseño personalizado para alta/baja de usuarios, empresas e informes con validación a nivel servidor y aislamiento por empresa.
- Roles empresariales reales con pruebas contra acceso cruzado. Mantener el Django Admin global solo para superusuarios.
- Registros de auditoría para concesión/revocación de permisos y cambios de enlaces.

## Iteración 3 — integración BI
- Crear 2 informes ficticios publicados desde cuenta comercial propia. Validar compatibilidad en iframe, móvil, filtros y tiempos de carga.
- Documentar que Publicar en web mantiene el recurso original público; no convertirlo en solución para datos privados.
- Probar navegadores y terceros contenidos de scripts / CSP.

## Iteración 4 — infraestructura (requiere autorización explícita)
- Repositorio GitHub privado, GitHub Actions pasando, PostgreSQL, servicio Railway y dominio con Cloudflare.
- Variables secretas, TLS, backups, rate-limits, monitoreo y costos.
