from fastapi import FastAPI, APIRouter, Request, HTTPException
# NEW BUILD MARKER
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
from typing import Dict, Any
import os

# Define la instancia de la aplicación FastAPI.
app = FastAPI(title="API Gateway Taller Microservicios")
logging.basicConfig(level=logging.INFO, format='[gateway] %(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Configura CORS (Cross-Origin Resource Sharing).
# Esto es esencial para permitir que el frontend se comunique con el gateway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (ajustar en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea un enrutador para las peticiones de los microservicios.
router = APIRouter(prefix="/api/v1")

# Define los microservicios y sus URLs.
# La URL debe coincidir con el nombre del servicio definido en docker-compose.yml.
# El puerto debe ser el del contenedor (ej. auth-service:8004).
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8004"),
    "restaurantes": os.getenv("RESTAURANTES_SERVICE_URL", "http://restaurantes-service:8001"),
    "reservas": os.getenv("RESERVAS_SERVICE_URL", "http://reservas-service:8003"),
    "menu": os.getenv("MENU_SERVICE_URL", "http://menu-service:8002"),
}

# Rutas genéricas para redirigir peticiones GET/POST/PUT/PATCH/DELETE a los microservicios.
@router.get("/{service_name}/{path:path}")
async def forward_get(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")
    
    service_url = f"{SERVICES[service_name]}/{path}"
    
    try:
        # Reenviar headers relevantes (incluye Authorization si está presente)
        headers = {k: v for k, v in request.headers.items()}
        timeout = float(os.getenv("GATEWAY_TIMEOUT", "5"))
        response = requests.get(service_url, params=request.query_params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.post("/{service_name}/{path:path}")
async def forward_post(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = f"{SERVICES[service_name]}/{path}"

    try:
        headers = {k: v for k, v in request.headers.items()}
        timeout = float(os.getenv("GATEWAY_TIMEOUT", "5"))
        content_type = request.headers.get("content-type", "").lower()
        params = request.query_params
        body = await request.body()
        logger.info(f"forward_post service={service_name} path={path} content_type={content_type} body_len={len(body)}")
        if "application/json" in content_type:
            import json as _json
            payload = _json.loads(body.decode("utf-8") or "{}") if body else {}
            response = requests.post(service_url, json=payload, params=params, headers=headers, timeout=timeout)
        else:
            # Pasar cuerpo crudo para formularios/multipart/otros
            response = requests.post(service_url, data=body, params=params, headers=headers, timeout=timeout)
        logger.info(f"forward_post upstream_status={response.status_code}")
        if response.status_code >= 400:
            # Propaga el código original y el texto de error
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json() if response.content else {"status": response.status_code}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.put("/{service_name}/{path:path}")
async def forward_put(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")
    service_url = f"{SERVICES[service_name]}/{path}"
    try:
        headers = {k: v for k, v in request.headers.items()}
        timeout = float(os.getenv("GATEWAY_TIMEOUT", "5"))
        content_type = headers.get("content-type", "").lower()
        params = request.query_params
        if "application/json" in content_type:
            payload = await request.json()
            response = requests.put(service_url, json=payload, params=params, headers=headers, timeout=timeout)
        else:
            body = await request.body()
            response = requests.put(service_url, data=body, params=params, headers=headers, timeout=timeout)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json() if response.content else {"status": response.status_code}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.patch("/{service_name}/{path:path}")
async def forward_patch(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")
    service_url = f"{SERVICES[service_name]}/{path}"
    try:
        headers = {k: v for k, v in request.headers.items()}
        timeout = float(os.getenv("GATEWAY_TIMEOUT", "5"))
        content_type = headers.get("content-type", "").lower()
        params = request.query_params
        if "application/json" in content_type:
            payload = await request.json()
            response = requests.patch(service_url, json=payload, params=params, headers=headers, timeout=timeout)
        else:
            body = await request.body()
            response = requests.patch(service_url, data=body, params=params, headers=headers, timeout=timeout)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json() if response.content else {"status": response.status_code}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.delete("/{service_name}/{path:path}")
async def forward_delete(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")
    service_url = f"{SERVICES[service_name]}/{path}"
    try:
        headers = {k: v for k, v in request.headers.items()}
        timeout = float(os.getenv("GATEWAY_TIMEOUT", "5"))
        response = requests.delete(service_url, params=request.query_params, headers=headers, timeout=timeout)
        if response.status_code == 204:
            return {"status": "deleted"}
        response.raise_for_status()
        return response.json() if response.content else {"status": response.status_code}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

# Incluye el router en la aplicación principal.
app.include_router(router)

# Endpoint de salud para verificar el estado del gateway.
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running."}
