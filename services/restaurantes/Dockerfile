FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecutar la aplicación FastAPI en el puerto 8003 (mappeado en docker-compose como 8003:8003)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
