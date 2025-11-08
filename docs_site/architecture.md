# Arquitectura del Sistema

Este documento describe la arquitectura de alto nivel del sistema de microservicios.

## Vista General
```mermaid
flowchart TB
    subgraph Cliente
        FE[Frontend Flask]
    end
    FE --> GW[API Gateway]
    subgraph Backend
        AUTH[Auth Service]
        REST[Restaurantes Service]
        MENU[Menú Service]
        RESV[Reservas Service]
    end
    GW --> AUTH
    GW --> REST
    GW --> MENU
    GW --> RESV
    AUTH --> MDB[(MongoDB)]
    REST --> PG[(PostgreSQL)]
    MENU --> PG
    RESV --> PG
    subgraph Infra
        INIT[Script Init DB]
    end
    INIT --> PG
```

## Patrones
- Separación de responsabilidades por dominio.
- Comunicación HTTP síncrona vía API Gateway.
- Persistencia mixta (SQL relacional y NoSQL para usuarios/tokens).

## Decisiones Clave
| Decisión | Justificación |
|----------|---------------|
| Remover FKs en código entre servicios | Evitar acoplamiento de metadata entre microservicios y permitir evolución independiente |
| Rotación de refresh tokens | Mitigar riesgo de reutilización y facilitar revocación inmediata |
| Uso de MongoDB para Auth | Flexibilidad en almacenamiento de tokens y documentos de usuario |
| API Gateway simple con `requests` | Reducción de complejidad inicial, facilita extensión incremental |

## Flujo de Autenticación
```mermaid
sequenceDiagram
    participant U as Usuario
    participant FE as Frontend
    participant GW as API Gateway
    participant AUTH as Auth Service

    U->>FE: Ingresa credenciales
    FE->>GW: POST /login
    GW->>AUTH: Forward /login
    AUTH-->>GW: access_token + refresh_token
    GW-->>FE: access_token + refresh_token
    FE->>GW: Solicita recurso protegido (Authorization: Bearer)
    GW->>REST: Forward con Authorization
    REST-->>GW: Datos
    GW-->>FE: Datos
```

## Flujo de Reserva
```mermaid
sequenceDiagram
    participant U as Usuario
    participant FE as Frontend
    participant GW as API Gateway
    participant RESV as Reservas Service
    participant REST as Restaurantes Service

    U->>FE: Selecciona fecha y restaurante
    FE->>GW: POST /reservas
    GW->>RESV: Forward /reservas
    RESV->>REST: (Opcional) Validar existencia restaurante
    REST-->>RESV: OK
    RESV-->>GW: Reserva creada
    GW-->>FE: Confirmación
```

## Consideraciones de Escalabilidad
- Separar base de datos para cada servicio si crece la carga.
- Incorporar caché (Redis) para listas de restaurantes y menús.
- Rate limiting en API Gateway.

## Futuras Extensiones
- Websockets para disponibilidad en tiempo real.
- Motor de recomendaciones de menú.
