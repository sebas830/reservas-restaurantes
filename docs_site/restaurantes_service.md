# Servicio de Restaurantes

## Endpoints Principales
- GET /restaurantes/
- GET /restaurantes/{id}
- POST /restaurantes/
- PUT /restaurantes/{id}
- DELETE /restaurantes/{id}

## Modelo SQL (resumen)
```mermaid
classDiagram
  class Restaurante {
    int id
    string nombre
    string direccion
    string tipo_cocina
    int capacidad
  }
```

## Notas
- Validaciones básicas de datos.
- Docker expone el puerto 8001.
