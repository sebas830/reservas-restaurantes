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
class Reserva(Base):
    """
    Modelo para gestionar las reservas de restaurantes.
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_nombre = Column(String(100), nullable=False)
    cliente_email = Column(String(100), nullable=False)
    cliente_telefono = Column(String(20))
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"), nullable=False)
    fecha_reserva = Column(DateTime, nullable=False)
    numero_personas = Column(Integer, nullable=False)
    estado = Column(String(20), default="pendiente")  # pendiente, confirmada, cancelada, completada
    notas = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Reserva(id={self.id}, cliente={self.cliente_nombre}, fecha={self.fecha_reserva}>"

# TODO: Define los modelos Pydantic para la validación de datos.
# Estos modelos se usarán en los endpoints de FastAPI para validar la entrada y salida.

class ReservaBase(BaseModel):
    cliente_nombre: str
    cliente_email: str
    cliente_telefono: Optional[str] = None
    restaurante_id: int
    fecha_reserva: datetime
    numero_personas: int
    notas: Optional[str] = None

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_telefono: Optional[str] = None
    restaurante_id: Optional[int] = None
    fecha_reserva: Optional[datetime] = None
    numero_personas: Optional[int] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

class ReservaRead(ReservaBase):
    id: int
    estado: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_telefono: Optional[str] = None
    fecha_reserva: Optional[datetime] = None
    numero_personas: Optional[int] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

class ReservaRead(ReservaBase):
    id: int
    estado: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True # Habilita la compatibilidad con ORM
