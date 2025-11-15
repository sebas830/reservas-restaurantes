FROM python:3.12-slim

WORKDIR /app

# Cuando el build context es la raíz del repo, apuntar a los archivos dentro de services/restaurantes
COPY services/restaurantes/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el contenido del servicio al directorio de trabajo
COPY services/restaurantes/ ./
# Copiar el paquete common al contenedor para que las imports relativas funcionen
COPY common/ ./common/

# Ejecutar la aplicación FastAPI en el puerto 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
