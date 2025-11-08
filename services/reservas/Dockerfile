FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero las dependencias
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente
COPY . .

# Expone el puerto 8003
EXPOSE 8003

# Comando para iniciar la app FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

