from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import os

import models
from database import get_db
import secrets
import logging
from common.helpers.utils import send_request_to_service

logger = logging.getLogger(__name__)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8004")

app = FastAPI(title="Restaurantes Service")


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Servicio de restaurantes en funcionamiento."}


@app.get("/health", tags=["root"])
def health_check():
    return {"status": "ok"}


@app.post("/restaurantes/", response_model=dict, tags=["restaurantes"])
def create_restaurante(rest: models.RestauranteCreate, db: Session = Depends(get_db)):
    """Crea un restaurante y opcionalmente registra el usuario propietario en el servicio de autenticación.

    Si `create_owner` es True y `owner_email` está presente, se intentará registrar el usuario en
    el servicio de autenticación interno. No se crearán cuentas externas (Gmail) desde aquí.
    """
    payload = rest.dict()
    # Extraer campos relacionados con la creación del usuario
    owner_password = payload.pop("owner_password", None)
    create_owner = payload.pop("create_owner", False)

    # Asegurarse de pasar sólo campos que existen en el modelo DB
    db_fields = {k: v for k, v in payload.items() if k in {
        "nombre", "direccion", "telefono", "capacidad", "tipo_cocina", "horario", "activo", "owner_email"
    }}

    new = models.Restaurante(**db_fields)
    db.add(new)
    db.commit()
    db.refresh(new)

    created_owner_password = None
    if create_owner and db_fields.get("owner_email"):
        # Generar contraseña segura si no se proporcionó
        created_owner_password = owner_password or secrets.token_urlsafe(10)
        auth_url = f"{AUTH_SERVICE_URL.rstrip('/')}/register"
        try:
            send_request_to_service(auth_url, method="POST", data={
                "email": db_fields.get("owner_email"),
                "password": created_owner_password,
                "full_name": db_fields.get("nombre"),
                "role": "restaurant"
            })
            logger.info(f"Usuario creado en auth-service para {db_fields.get('owner_email')}")
        except Exception as e:
            # No revertimos la creación del restaurante si falla la creación del usuario,
            # pero informamos del error para que el operador lo gestione.
            logger.warning(f"Fallo al crear usuario en auth-service: {e}")

    # Construir representación serializable del restaurante
    rest_data = {c.name: getattr(new, c.name) for c in new.__table__.columns}
    result = {"restaurante": rest_data}
    if created_owner_password:
        result["owner_initial_password"] = created_owner_password

    return result


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

