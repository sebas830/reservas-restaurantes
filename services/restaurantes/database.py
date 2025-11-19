import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida en variables de entorno")

# Usar pool_pre_ping para detectar conexiones muertas y evitar errores por sockets cerrados
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(timeout: int = 30):
    """Bloquea hasta que la base de datos responda o hasta agotar el timeout (segundos).

    Esto evita que el servicio responda con 500 en las primeras peticiones si Postgres aún
    no ha terminado de arrancar. Se usa en el evento de startup del servicio.
    """
    start = time.time()
    last_exc = None
    while time.time() - start < timeout:
        try:
            # Intentar una conexión rápida
            with engine.connect() as conn:
                # exec_driver_sql es el método correcto para ejecutar sentencias SQL crudas
                conn.exec_driver_sql("SELECT 1")
            return True
        except Exception as e:
            last_exc = e
            time.sleep(1)
    # Si aquí falla, propagar la última excepción para ser registrada por el servicio
    raise RuntimeError(f"No se pudo conectar a la base de datos en {timeout}s: {last_exc}")
