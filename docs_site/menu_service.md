# Servicio de Menú

## Endpoints
- GET /platos/
- GET /platos/{id}
- POST /platos/
- PUT /platos/{id}
- DELETE /platos/{id}

## Modelo Plato
```mermaid
classDiagram
  class Plato {
    int id
    string nombre
    string descripcion
    float precio
    int restaurante_id
  }
```

## Mejoras Futuras
- Menú del día.
- Filtros por categoría.
