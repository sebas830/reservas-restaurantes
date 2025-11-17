# Cambios (Changelog)

**Nota (Nov 2025)**: Cambios recientes: `scripts/init_db.py` ahora es idempotente para evitar duplicados de restaurantes en reinicios; se añadió `scripts/cleanup_duplicates.py` para detectar y consolidar duplicados (ejecutar dry-run primero). Hacer backup antes de aplicar cambios destructivos. Más detalle en `docs/AUDITORIA.md`.

Este archivo resume cambios clave recientes. Para detalle completo ver la sección de auditoría.

## Últimos Cambios Destacados
- Autenticación: Rotación y revocación de refresh tokens implementada.
- API Gateway: Reenvío de Authorization y soporte para todos los métodos comunes.
- Documentación: Estructura inicial con MkDocs y diagramas Mermaid.
- Tests: Flujo de autenticación automatizado con pytest (1 test verde).
