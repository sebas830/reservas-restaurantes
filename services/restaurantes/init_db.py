import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from models import Base

def ensure_database_exists(database_url: str):
    # Conecta al DB admin (postgres) para crear la base si no existe
    from sqlalchemy.engine.url import make_url

    url = make_url(database_url)
    target_db = url.database
    # usar 'postgres' para la conexión administrativa
    admin_url = url.set(database="postgres")

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        # Crear la base de datos si no existe
        try:
            conn.execute(text(f"CREATE DATABASE \"{target_db}\"") )
            print(f"Base de datos '{target_db}' creada.")
        except ProgrammingError as e:
            # si existe o no se puede crear, mostrar info
            msg = str(e)
            if 'already exists' in msg:
                print(f"La base de datos '{target_db}' ya existe.")
            else:
                print("Advertencia al crear la base de datos:", e)


def create_tables(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas/actualizadas correctamente en", database_url)


if __name__ == '__main__':
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL no definida')

    ensure_database_exists(database_url)
    create_tables(database_url)
