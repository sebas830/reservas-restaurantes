from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

from models import Base, Plato, PlatoCreate, PlatoRead, PlatoUpdate
from database import engine, SessionLocal

# Crear las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio de Menú",
    description="API para gestionar el menú de los restaurantes",
    version="1.0.0"
)

# Dependencia para obtener la sesión de base de datos
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
        "message": "Servicio de menú en funcionamiento",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Status"])
def health_check():
    """Endpoint para health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ENDPOINTS CRUD

@app.post("/platos/", response_model=PlatoRead, tags=["Platos"])
def crear_plato(plato: PlatoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo plato en el menú.
    
    - **nombre**: Nombre del plato (requerido)
    - **descripcion**: Descripción detallada del plato
    - **precio**: Precio del plato (requerido, > 0)
    - **categoria**: Categoría del plato (ej. Entrada, Plato Principal)
    - **disponible**: Si el plato está disponible en el menú
    - **restaurante_id**: ID del restaurante al que pertenece el plato
    """
    nuevo_plato = Plato(**plato.dict())
    db.add(nuevo_plato)
    try:
        db.commit()
        db.refresh(nuevo_plato)
        return nuevo_plato
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/platos/", response_model=List[PlatoRead], tags=["Platos"])
def obtener_platos(
    restaurante_id: Optional[int] = None,
    categoria: Optional[str] = None,
    disponible: Optional[bool] = None,
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de platos con filtros opcionales.
    
    - **restaurante_id**: Filtrar por restaurante
    - **categoria**: Filtrar por categoría
    - **disponible**: Filtrar por disponibilidad
    - **search**: Buscar en nombre o descripción
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    query = db.query(Plato)
    
    if restaurante_id:
        query = query.filter(Plato.restaurante_id == restaurante_id)
    if categoria:
        query = query.filter(Plato.categoria == categoria)
    if disponible is not None:
        query = query.filter(Plato.disponible == disponible)
    if search:
        query = query.filter(
            or_(
                Plato.nombre.ilike(f"%{search}%"),
                Plato.descripcion.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()

@app.get("/platos/{plato_id}", response_model=PlatoRead, tags=["Platos"])
def obtener_plato(plato_id: int, db: Session = Depends(get_db)):
    """
    Obtener un plato específico por su ID.
    
    - **plato_id**: ID del plato a obtener
    """
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if plato is None:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return plato

@app.put("/platos/{plato_id}", response_model=PlatoRead, tags=["Platos"])
def actualizar_plato(
    plato_id: int,
    plato_update: PlatoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un plato existente.
    
    - **plato_id**: ID del plato a actualizar
    - **plato_update**: Datos a actualizar (todos los campos son opcionales)
    """
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if plato is None:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_data = plato_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plato, field, value)
    
    try:
        db.commit()
        db.refresh(plato)
        return plato
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/platos/{plato_id}", status_code=204, tags=["Platos"])
def eliminar_plato(plato_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un plato del menú.
    
    - **plato_id**: ID del plato a eliminar
    """
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if plato is None:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    try:
        db.delete(plato)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
