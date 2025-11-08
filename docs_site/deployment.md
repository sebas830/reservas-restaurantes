# Despliegue

## Requisitos
- Docker y Docker Compose
- Variables de entorno en `.env`

## Pasos
1. Construir e iniciar servicios:
```bash
docker-compose up -d --build
```
2. Verificar health checks:
```bash
curl http://localhost:8000/health
```
3. Acceder al Frontend:
- http://localhost:5000

## Documentación MkDocs
Para servir la documentación localmente:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```
La documentación se servirá en http://127.0.0.1:8000 (puerto de mkdocs).
