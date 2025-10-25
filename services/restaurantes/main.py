from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import os

import models
from database import get_db

app = FastAPI(title="Restaurantes Service")


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Servicio de restaurantes en funcionamiento."}


@app.get("/health", tags=["root"])
def health_check():
    return {"status": "ok"}


@app.post("/restaurantes/", response_model=models.RestauranteRead, tags=["restaurantes"])
def create_restaurante(rest: models.RestauranteCreate, db: Session = Depends(get_db)):
    new = models.Restaurante(**rest.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@app.get("/restaurantes/", response_model=List[models.RestauranteRead], tags=["restaurantes"])
def list_restaurantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Restaurante).offset(skip).limit(limit).all()
    return items


@app.get("/restaurantes/{rest_id}", response_model=models.RestauranteRead, tags=["restaurantes"])
def get_restaurante(rest_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Restaurante).filter(models.Restaurante.id == rest_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return item


@app.put("/restaurantes/{rest_id}", response_model=models.RestauranteRead, tags=["restaurantes"])
def update_restaurante(rest_id: int, rest: models.RestauranteUpdate, db: Session = Depends(get_db)):
    item = db.query(models.Restaurante).filter(models.Restaurante.id == rest_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    for k, v in rest.dict(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/restaurantes/{rest_id}", tags=["restaurantes"])
def delete_restaurante(rest_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Restaurante).filter(models.Restaurante.id == rest_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    db.delete(item)
    db.commit()
    return {"detail": "El restaurante ha sido eliminado"}

