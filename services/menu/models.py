from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

Base = declarative_base()

class Plato(Base):
    __tablename__ = "platos"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey('restaurantes.id'), nullable=False)
    nombre = Column(String(150), nullable=False, index=True)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    categoria = Column(String(100))
    disponible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Plato(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"

class PlatoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    disponible: Optional[bool] = True
    restaurante_id: int

    @validator('precio')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor que 0')
        return round(v, 2)  # Redondear a 2 decimales
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

