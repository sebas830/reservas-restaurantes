import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
# Esto asegura que las configuraciones se obtengan desde el entorno de ejecución,
# lo que es una buena práctica para entornos de desarrollo y producción.
load_dotenv()

# TODO: Define una clase para agrupar las configuraciones.
class Settings:
    """Clase para gestionar las configuraciones de la aplicación."""
    
    # URLs de los servicios
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    # Configuración de la base de datos
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password123")
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "reservas_db")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # TODO: Agrega otras configuraciones globales.
    # Por ejemplo, una clave secreta para la autenticación o el token JWT.
    # SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-segura")
    # ALGORITHM: str = "HS256"

# Crea una instancia de la clase de configuración.
settings = Settings()

# --------------------------------------------------------------------------
# Los estudiantes pueden importar este objeto settings en cualquier parte 
# de su código para acceder a las configuraciones de manera consistente.
# 
# Ejemplo de uso en un microservicio
# from common.config import settings
# 
# Ahora puedes acceder a las variables de configuración
# api_url = settings.API_GATEWAY_URL
# 