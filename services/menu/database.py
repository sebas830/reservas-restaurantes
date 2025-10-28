from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Puedes usar SQLite mientras desarrollas
DATABASE_URL = "sqlite:///./menu.db"

# Si luego usas PostgreSQL, será algo como:
# DATABASE_URL = "postgresql://usuario:password@db/menu"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
