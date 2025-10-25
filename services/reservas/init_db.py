from models import Base
from database import engine

def init_db():
    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    init_db()
    print("¡Base de datos inicializada correctamente!")