# Pruebas

**Nota (Nov 2025)**: Cambios recientes: se actualizó el init de BD para ser idempotente (`scripts/init_db.py`) y se añadió `scripts/cleanup_duplicates.py` para detectar/limpiar restaurantes duplicados. Antes de ejecutar pruebas que toquen datos de la BD en modo `--apply` haga un backup o use un entorno aislado.

## Pruebas Manuales
- curl a `/health` de cada servicio.
- Flujos básicos: crear restaurante, crear plato, crear reserva.

## Pruebas Automatizadas (pytest)
- `tests/test_auth.py` valida el flujo completo de autenticación (register/login/refresh/logout).

### Ejecutar pruebas en contenedor
```bash
docker run --rm --network reservas-restaurantes_default \
  -v "$(pwd)":/app -w /app \
  reservas-restaurantes_auth-service:latest \
  bash -c "pip install -q pytest requests && PYTHONPATH=/app pytest -q tests/test_auth.py"
```

El resultado esperado: `1 passed`.
