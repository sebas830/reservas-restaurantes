from fastapi import FastAPI, APIRouter, HTTPException
import os

# TODO: Importar el módulo de base de datos y los modelos
# from .database import [tu_motor_de_base_de_datos]
# from .models import [tus_modelos]

# TODO: Configurar la URL de la base de datos desde las variables de entorno
# DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# TODO: Crea una instancia del router para organizar los endpoints
router = APIRouter()

# TODO: Define un endpoint raíz o de salud para verificar que el servicio está funcionando
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

from models import Reserva, ReservaCreate, ReservaUpdate, ReservaRead, Base
from database import SessionLocal, engine

# Las tablas son creadas por el script de inicialización
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio de Reservas",
    description="API para gestionar las reservas de los restaurantes",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Status"])
def read_root():
    """Verificar que el servicio está en funcionamiento"""
    return {
        "message": "Servicio de reservas en funcionamiento",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Status"])
def health_check():
    """Endpoint para health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/reservas/", response_model=ReservaRead, tags=["Reservas"])
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva reserva.
    
    - **cliente_nombre**: Nombre del cliente
    - **cliente_email**: Email del cliente
    - **cliente_telefono**: Teléfono del cliente (opcional)
    - **restaurante_id**: ID del restaurante
    - **fecha_reserva**: Fecha y hora de la reserva
    - **numero_personas**: Número de personas
    - **notas**: Notas adicionales (opcional)
    """
    # Validar que la fecha no sea en el pasado
    if reserva.fecha_reserva < datetime.now():
        raise HTTPException(status_code=400, detail="La fecha de reserva no puede ser en el pasado")
    
    # Validar disponibilidad
    reservas_existentes = db.query(Reserva).filter(
        and_(
            Reserva.restaurante_id == reserva.restaurante_id,
            Reserva.fecha_reserva.between(
                reserva.fecha_reserva - timedelta(hours=2),
                reserva.fecha_reserva + timedelta(hours=2)
            ),
            Reserva.estado != "cancelada"
        )
    ).count()
    
    if reservas_existentes >= 3:  # Límite de reservas por franja horaria
        raise HTTPException(status_code=400, detail="No hay disponibilidad en ese horario")
    
    nueva_reserva = Reserva(**reserva.dict())
    db.add(nueva_reserva)
    try:
        db.commit()
        db.refresh(nueva_reserva)
        return nueva_reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reservas/", response_model=List[ReservaRead], tags=["Reservas"])
def obtener_reservas(
    restaurante_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    cliente_email: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de reservas con filtros opcionales.
    
    - **restaurante_id**: Filtrar por restaurante
    - **estado**: Filtrar por estado de la reserva
    - **fecha_inicio**: Fecha inicial para filtrar
    - **fecha_fin**: Fecha final para filtrar
    - **cliente_email**: Filtrar por email del cliente
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    query = db.query(Reserva)
    
    if restaurante_id:
        query = query.filter(Reserva.restaurante_id == restaurante_id)
    if estado:
        query = query.filter(Reserva.estado == estado)
    if fecha_inicio:
        query = query.filter(Reserva.fecha_reserva >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Reserva.fecha_reserva <= fecha_fin)
    if cliente_email:
        query = query.filter(Reserva.cliente_email == cliente_email)
    
    return query.offset(skip).limit(limit).all()

@app.get("/reservas/{reserva_id}", response_model=ReservaRead, tags=["Reservas"])
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """
    Obtener una reserva específica por su ID.
    
    - **reserva_id**: ID de la reserva a obtener
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@app.put("/reservas/{reserva_id}", response_model=ReservaRead, tags=["Reservas"])
def actualizar_reserva(
    reserva_id: int,
    reserva_update: ReservaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una reserva existente.
    
    - **reserva_id**: ID de la reserva a actualizar
    - **reserva_update**: Datos a actualizar (todos los campos son opcionales)
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    update_data = reserva_update.dict(exclude_unset=True)
    
    # Validaciones adicionales si se actualiza la fecha
    if "fecha_reserva" in update_data:
        if update_data["fecha_reserva"] < datetime.now():
            raise HTTPException(status_code=400, detail="La fecha de reserva no puede ser en el pasado")
    
    for field, value in update_data.items():
        setattr(reserva, field, value)
    
    try:
        db.commit()
        db.refresh(reserva)
        return reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/reservas/{reserva_id}", status_code=204, tags=["Reservas"])
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """
    Cancelar/eliminar una reserva.
    
    - **reserva_id**: ID de la reserva a cancelar
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # En lugar de eliminar, marcamos como cancelada
    reserva.estado = "cancelada"
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/reservas/{reserva_id}/estado", response_model=ReservaRead, tags=["Reservas"])
def actualizar_estado_reserva(
    reserva_id: int,
    estado: str = Query(..., regex="^(pendiente|confirmada|cancelada|completada)$"),
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de una reserva.
    
    - **reserva_id**: ID de la reserva
    - **estado**: Nuevo estado (pendiente, confirmada, cancelada, completada)
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    reserva.estado = estado
    try:
        db.commit()
        db.refresh(reserva)
        return reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# TODO: Implementa los endpoints de tu microservicio aquí
# Ejemplo de un endpoint GET:
# @router.get("/[ruta_del_recurso]/")
# async def get_[recurso]():
#     # TODO: Agrega la lógica de tu negocio aquí
#     return {"data": "Aquí van tus datos."}

# Ejemplo de un endpoint POST:
# @router.post("/[ruta_del_recurso]/")
# async def create_[recurso](item: [tu_modelo_pydantic]):
#     # TODO: Agrega la lógica para crear un nuevo recurso
#     return {"message": "[recurso] creado exitosamente."}


# TODO: Incluir el router en la aplicación principal
# app.include_router(router, prefix="/api/v1")
