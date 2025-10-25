from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
Base = declarative_base()

# TODO: Crea tus modelos de datos aquí.
# Cada clase de modelo representa una tabla en tu base de datos.
# Debes renombrar YourModel por el nombre de la Clase según el servicio
class Restaurante(Base):
    """
    Modelo para la tabla `restaurantes`.
    Contiene la información básica necesaria para relacionar reservas.
    """
    __tablename__ = "restaurantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(250))
    telefono = Column(String(50))
    capacidad = Column(Integer, nullable=True)
    tipo_cocina = Column(String(100), nullable=True)
    horario = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Restaurante(id={self.id}, nombre='{self.nombre}')>"

# TODO: Define los modelos Pydantic para la validación de datos.
# Estos modelos se usarán en los endpoints de FastAPI para validar la entrada y salida.

class RestauranteBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    capacidad: Optional[int] = None
    tipo_cocina: Optional[str] = None
    horario: Optional[str] = None
    activo: Optional[bool] = True


class RestauranteCreate(RestauranteBase):
    pass


class RestauranteUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    capacidad: Optional[int] = None
    tipo_cocina: Optional[str] = None
    horario: Optional[str] = None
    activo: Optional[bool] = None


class RestauranteRead(RestauranteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
