# Sistema de Reservas de Restaurantes - Microservicios

| Código | Nombre | Correo |
|:---|:---|:---|
| 1117012905 | Sebastian Ramirez Parra | sebastian.ramirez.2905@miremington.edu.co |
| 1113656983 | Harold Piedrahita | harold.piedrahita.6983@miremington.edu.co |

---

## Descripción

Sistema de gestión de reservas para restaurantes implementado con arquitectura de microservicios. Permite administrar restaurantes, menús y reservas a través de una API REST.

## Arquitectura

- **API Gateway** (Puerto 8000): Punto de entrada único
- **Servicio de Autenticación** (Puerto 8004): Gestión de usuarios (MongoDB)
- **Servicio de Restaurantes** (Puerto 8001): CRUD de restaurantes (PostgreSQL)
- **Servicio de Menú** (Puerto 8002): Gestión de platos (PostgreSQL)
- **Servicio de Reservas** (Puerto 8003): Gestión de reservas (PostgreSQL)
- **Frontend** (Puerto 5000): Interfaz web (Flask)

## Inicio Rápido

### Prerrequisitos

- Docker
- Docker Compose

### Instalación

1. Clonar el repositorio:
    ```bash
    git clone https://github.com/sebas830/reservas-restaurantes.git
    cd reservas-restaurantes
    ```

2. Configurar variables de entorno:
    ```bash
    cp _env.example .env
    # Editar .env con tus configuraciones
    ```

3. Levantar todos los servicios:
    ```bash
    docker-compose up -d
    ```

4. Inicializar la base de datos (automático al arrancar):
    ```bash
    # El script init_db.py se ejecuta automáticamente
    # Para ejecutarlo manualmente:
    docker run --rm --network reservas-restaurantes_default \
      -v $(pwd)/scripts:/app \
      -e POSTGRES_HOST=postgres \
      -e POSTGRES_DB=reserva \
      -e POSTGRES_USER=admin \
      -e POSTGRES_PASSWORD=password123 \
      python:3.9-slim bash -c "pip install psycopg2-binary && python /app/init_db.py"
    ```

5. Verificar servicios:
    ```bash
    docker ps
    ```

## Uso

### Endpoints Principales

**API Gateway**: `http://localhost:8000`
- Health: `GET /health`
- Restaurantes: `GET /api/v1/restaurantes/restaurantes/`
- Reservas: `GET /api/v1/reservas/reservas/`

**Servicio Restaurantes**: `http://localhost:8001`
- Listar: `GET /restaurantes/`
- Crear: `POST /restaurantes/`
- Obtener: `GET /restaurantes/{id}`
- Actualizar: `PUT /restaurantes/{id}`
- Eliminar: `DELETE /restaurantes/{id}`

**Servicio Reservas**: `http://localhost:8003`
- Listar: `GET /reservas/`
- Crear: `POST /reservas/`
- Obtener: `GET /reservas/{id}`

**Frontend**: `http://localhost:5000`

### Ejemplo de Uso

```bash
# Listar restaurantes
curl http://localhost:8001/restaurantes/

# Crear un restaurante
curl -X POST http://localhost:8001/restaurantes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Mi Restaurante","direccion":"Calle 123","telefono":"555-0000","capacidad":50,"tipo_cocina":"Italiana","horario":"11:00-22:00"}'
```

## Documentación Detallada

La documentación ahora se genera con **MkDocs + Material** y diagramas **Mermaid**.

### Servir localmente
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```
Accede en: http://127.0.0.1:8000

### Build estático
```bash
mkdocs build
```
Genera el sitio en `site/`.

### Despliegue (GitHub Pages)
Si se configura un workflow, se puede publicar con:
```bash
mkdocs gh-deploy --force
```
*(Requiere permisos y configuración de Pages en el repositorio)*

## Tecnologías

- **Backend**: FastAPI, Python 3.9+
- **Bases de Datos**: PostgreSQL, MongoDB
- **Frontend**: Flask, Jinja2
- **Contenedores**: Docker, Docker Compose
- **ORM**: SQLAlchemy
- **Validación**: Pydantic

## Estado del Proyecto (Resumen)

| Módulo | Estado |
|--------|--------|
| Restaurantes | ✅ CRUD completo |
| Reservas | ✅ Completo (validaciones y CRUD) |
| Menú | ✅ Estable (CRUD, mejoras pendientes) |
| Autenticación | ✅ Tokens, refresh, rotación, logout |
| API Gateway | ✅ Forward GET/POST/PUT/PATCH/DELETE + Authorization |
| Frontend | 🔧 Básico (pendiente de expansión) |
| Infraestructura | ✅ Docker Compose y DB init |
| Documentación | ✅ 85% (MkDocs + Mermaid) |

## Licencia

MIT
