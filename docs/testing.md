# Pruebas

**Nota (Nov 2025)**: Cambios recientes: se actualizó el init de BD para ser idempotente (`scripts/init_db.py`) y se añadió `scripts/cleanup_duplicates.py` para detectar/limpiar restaurantes duplicados. Antes de ejecutar pruebas que toquen datos de la BD en modo `--apply` haga un backup o use un entorno aislado.

## Pruebas Manuales
- curl a `/health` de cada servicio.
- Flujos básicos: crear restaurante, crear plato, crear reserva.

## Pruebas Automatizadas (pytest)

### Suite de Tests de Autenticación
El archivo `tests/test_auth.py` contiene 7 tests que validan el flujo completo de autenticación:
- Registro de usuario
- Login exitoso con emisión de tokens
- Rotación de refresh tokens
- Revocación de tokens viejos
- Logout y revocación de sesión
- Rechazo de credenciales inválidas
- Health check del servicio

### Ejecutar pruebas desde el host (recomendado)
```bash
# Asegúrate de que los contenedores están corriendo: docker compose up -d
# Luego ejecuta:
pytest tests/test_auth.py -v
```

**Resultado esperado**: `7 passed in ~0.6s`

### Ejecutar pruebas en contenedor (alternativo)
```bash
docker run --rm --network reservas-restaurantes_default \
  -v "$(pwd)":/app -w /app \
  --entrypoint bash \
  reservas-restaurantes-auth-service:latest \
  -c "pip install -q pytest requests && PYTHONPATH=/app AUTH_URL=http://auth-service:8004 pytest -v tests/test_auth.py"
```

### Notas sobre los tests
- Los tests usan `localhost:8004` por defecto (ejecución desde host).
- Para ejecución dentro de Docker, configura `AUTH_URL=http://auth-service:8004`.
- Cada test genera un usuario único con UUID para evitar conflictos en ejecuciones múltiples.
- Los tests son idempotentes y pueden ejecutarse repetidamente sin efectos secundarios.
