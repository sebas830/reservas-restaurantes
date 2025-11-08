# Sistema de Reservas de Restaurantes

Bienvenido a la documentación oficial del sistema de microservicios para la gestión de restaurantes, menús y reservas.

## Objetivos
- Centralizar información técnica.
- Facilitar onboarding de nuevos desarrolladores.
- Definir claramente contratos de API y arquitectura.

## Vista Rápida de la Arquitectura
```mermaid
flowchart LR
    A[Frontend] --> B[API Gateway]
    B --> C[Servicio Autenticación]
    B --> D[Servicio Restaurantes]
    B --> E[Servicio Menú]
    B --> F[Servicio Reservas]
    C -->|MongoDB| M[(MongoDB)]
    D -->|PostgreSQL| P[(PostgreSQL)]
    E -->|PostgreSQL| P
    F -->|PostgreSQL| P
```

## Tecnologías Principales
- Python / FastAPI
- PostgreSQL & MongoDB
- Docker & Docker Compose
- JWT (Autenticación)
- MkDocs Material (Documentación)

## Estado Actual
Consultar la sección de Auditoría para progreso detallado.
