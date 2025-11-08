# Base de Datos

## Resumen
PostgreSQL central (actualmente compartida) y MongoDB para autenticación.

## Diagrama ER Simplificado
```mermaid
erDiagram
  RESTAURANTE ||--o{ PLATO : contiene
  RESTAURANTE ||--o{ RESERVA : tiene
  RESTAURANTE {
    int id PK
    string nombre
    string direccion
  }
  PLATO {
    int id PK
    string nombre
    float precio
    int restaurante_id FK
  }
  RESERVA {
    int id PK
    int restaurante_id FK
    string cliente
    datetime fecha
  }
```

## MongoDB (Auth)
Colecciones:
- users
- refresh_tokens

## Inicialización
`/scripts/init_db.py` crea tablas y datos de prueba.
