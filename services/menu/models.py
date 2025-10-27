from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
Base = declarative_base()

# TODO: Crea tus modelos de datos aquí.
# Cada clase de modelo representa una tabla en tu base de datos.
# Debes renombrar YourModel por el nombre de la Clase según el servicio
class Plato(Base):
    """
    Modelo de datos que representa un plato del menú del restaurante.
    Ajusta esta clase según los requisitos de tu aplicación.
    """
    __tablename__ = "platos"  # Nombre de la tabla en la base de datos

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)  # Nombre del plato
    descripcion = Column(String)  # Descripción del plato
    precio = Column(Float, nullable=False)  # Precio del plato
    disponible = Column(Boolean, default=True)  # Indica si está disponible en el menú
    creada_en = Column(DateTime, default=datetime.utcnow)  # Fecha de creación

    # TODO: Agrega más columnas según sea necesario.
    # Por ejemplo:
    # categoria = Column(String)  # Categoría del plato (ej. Bebidas, Entradas)
    # imagen_url = Column(String)  # Imagen del plato

    def __repr__(self):
        return f"<Plato(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"

# TODO: Define los modelos Pydantic para la validación de datos.
# Estos modelos se usarán en los endpoints de FastAPI para validar la entrada y salida.

class PlatoBase(BaseModel):
    """
    Modelo base de Pydantic para representar los datos comunes de un plato.
    Se usa para crear y actualizar registros.
    """
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    disponible: Optional[bool] = True
    # TODO: Agrega los campos que se necesitan para crear o actualizar un recurso.
    # Ejemplo:
    # categoria: Optional[str] = None

class PlatoCreate(PlatoBase):
    """
    Modelo Pydantic usado para crear un nuevo plato.
    """
    pass

class PlatoRead(PlatoBase):
    """
    Modelo Pydantic usado para mostrar los datos de un plato en las respuestas.
    Incluye los campos generados automáticamente, como 'id' y 'creada_en'.
    """
    id: int
    creada_en: datetime

    class Config:
        orm_mode = True  # Habilita la compatibilidad con ORM (SQLAlchemy)

