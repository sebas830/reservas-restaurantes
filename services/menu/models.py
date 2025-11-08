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
    # Evitamos ForeignKey a nivel ORM para desacoplar metadatos entre servicios.
    # La FK se valida en PostgreSQL.
    restaurante_id = Column(Integer, nullable=False)
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
    created_at: datetime
    updated_at: datetime

    class Config:
        # Compatibilidad Pydantic v2
        from_attributes = True

class PlatoUpdate(BaseModel):
    """
    Modelo Pydantic usado para actualizar un plato existente.
    Todos los campos son opcionales.
    """
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    disponible: Optional[bool] = None
    restaurante_id: Optional[int] = None

    @validator('precio')
    def validar_precio(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El precio debe ser mayor que 0')
        if v is not None:
            return round(v, 2)
        return v
