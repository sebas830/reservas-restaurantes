from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from models import Base, Plato, PlatoCreate, PlatoRead
from database import engine, SessionLocal

# Crear las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Servicio de Menú del Restaurante")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Servicio de menú en funcionamiento."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ENDPOINTS CRUD

@app.post("/platos/", response_model=PlatoRead)
def crear_plato(plato: PlatoCreate, db: Session = Depends(get_db)):
    nuevo_plato = Plato(**plato.dict())
    db.add(nuevo_plato)
    db.commit()
    db.refresh(nuevo_plato)
    return nuevo_plato


@app.get("/platos/", response_model=List[PlatoRead])
def obtener_platos(db: Session = Depends(get_db)):
    return db.query(Plato).all()


@app.get("/platos/{plato_id}", response_model=PlatoRead)
def obtener_plato(plato_id: int, db: Session = Depends(get_db)):
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return plato


@app.put("/platos/{plato_id}", response_model=PlatoRead)
def actualizar_plato(plato_id: int, plato_data: PlatoCreate, db: Session = Depends(get_db)):
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    for key, value in plato_data.dict().items():
        setattr(plato, key, value)
    db.commit()
    db.refresh(plato)
    return plato


@app.delete("/platos/{plato_id}")
def eliminar_plato(plato_id: int, db: Session = Depends(get_db)):
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    db.delete(plato)
    db.commit()
    return {"message": f"Plato '{plato.nombre}' eliminado correctamente."}
