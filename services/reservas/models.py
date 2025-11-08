from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
Base = declarative_base()

class Reserva(Base):
    """
    Modelo SQLAlchemy para gestionar las reservas de restaurantes.
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_nombre = Column(String(100), nullable=False)
    cliente_email = Column(String(100), nullable=False)
    cliente_telefono = Column(String(20))
    # Nota: evitamos declarar ForeignKey a nivel de ORM para no acoplar metadatos entre microservicios.
    # La restricción de FK existe en la base de datos y será validada por PostgreSQL.
    restaurante_id = Column(Integer, nullable=False)
    fecha_reserva = Column(DateTime, nullable=False)
    numero_personas = Column(Integer, nullable=False)
    estado = Column(String(20), default="pendiente")  # pendiente, confirmada, cancelada, completada
    notas = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Reserva(id={self.id}, cliente={self.cliente_nombre}, fecha={self.fecha_reserva})>"


# Modelos Pydantic para validación de datos

class ReservaBase(BaseModel):
    """Modelo base con campos comunes para las reservas."""
    cliente_nombre: str
    cliente_email: str
    cliente_telefono: Optional[str] = None
    restaurante_id: int
    fecha_reserva: datetime
    numero_personas: int
    notas: Optional[str] = None


class ReservaCreate(ReservaBase):
    """Modelo para crear una nueva reserva."""
    pass


class ReservaUpdate(BaseModel):
    """Modelo para actualizar una reserva existente. Todos los campos son opcionales."""
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_telefono: Optional[str] = None
    restaurante_id: Optional[int] = None
    fecha_reserva: Optional[datetime] = None
    numero_personas: Optional[int] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


class ReservaRead(ReservaBase):
    """Modelo para leer una reserva con todos sus campos."""
    id: int
    estado: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # Compatibilidad Pydantic v2
        from_attributes = True
