import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Usar la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:password123@localhost:5433/reserva"
)

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear una clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()