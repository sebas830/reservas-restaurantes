import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Usar la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:password123@localhost:5433/reserva"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
