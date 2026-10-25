# Instrucciones para Codex / Claude Code

Proyecto: GABO PORTAL BI comercial. **Jamás** mezclar con activos institucionales, OpenBI, servicios de caja ni fuentes financieras reales. Mantener privacidad del repositorio.

1. Primero ejecutar pruebas y leer `docs/ARQUITECTURA.md`.
2. No hacer push sobre otras repositorios ni modificar infraestructura ajena.
3. Toda demo debe usar datos ficticios.
4. No publicar ni activar despliegues Railway/Cloudflare sin autorización explícita.
5. Los informes Power BI publicados en web son públicos, incluso detrás del login.
6. Antes de aceptar cambios: `python manage.py check`, `python manage.py makemigrations --check`, `python manage.py test`; pruebas en navegador para cambios de UI.
7. No introducir secretos ni tokens en commits.
