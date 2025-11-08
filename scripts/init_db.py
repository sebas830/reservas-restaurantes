import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "reserva"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password123"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

def wait_for_db(max_retries=30, retry_interval=2):
    """Esperar a que la base de datos esté disponible"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            logger.info("Conexión exitosa a la base de datos")
            return True
        except psycopg2.OperationalError as e:
            retry_count += 1
            wait_time = retry_interval * (2 ** (retry_count - 1))  # Retroceso exponencial
            logger.warning(f"Intento {retry_count}/{max_retries}. Esperando {wait_time}s. Error: {str(e)}")
            time.sleep(wait_time)
    
    logger.error("No se pudo establecer conexión con la base de datos")
    return False

def create_tables():
    """Crear las tablas necesarias en la base de datos"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Tabla de Restaurantes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurantes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            direccion VARCHAR(250),
            telefono VARCHAR(50),
            capacidad INTEGER,
            tipo_cocina VARCHAR(100),
            horario VARCHAR(100),
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de Platos (Menú)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS platos (
            id SERIAL PRIMARY KEY,
            restaurante_id INTEGER REFERENCES restaurantes(id) ON DELETE CASCADE,
            nombre VARCHAR(150) NOT NULL,
            descripcion VARCHAR(500),
            precio NUMERIC(10,2) NOT NULL,
            categoria VARCHAR(100),
            disponible BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de Reservas
        cur.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id SERIAL PRIMARY KEY,
            cliente_nombre VARCHAR(100) NOT NULL,
            cliente_email VARCHAR(100) NOT NULL,
            cliente_telefono VARCHAR(20),
            restaurante_id INTEGER REFERENCES restaurantes(id) ON DELETE CASCADE,
            fecha_reserva TIMESTAMP NOT NULL,
            numero_personas INTEGER NOT NULL,
            estado VARCHAR(20) DEFAULT 'pendiente',
            notas VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        logger.info("Tablas creadas exitosamente")
        
    except Exception as e:
        logger.error(f"Error creando las tablas: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

def insert_sample_data():
    """Insertar datos de prueba en las tablas"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Insertar restaurantes de prueba
        cur.execute("""
        INSERT INTO restaurantes (nombre, direccion, telefono, capacidad, tipo_cocina, horario) VALUES
        ('La Parrilla Dorada', 'Calle 123 #45-67', '555-0123', 50, 'Asados', '11:00-22:00'),
        ('Sabores del Mar', 'Av Principal 89-12', '555-0124', 40, 'Mariscos', '12:00-23:00'),
        ('Pasta Bella', 'Plaza Central 34-56', '555-0125', 35, 'Italiana', '11:30-22:30')
        ON CONFLICT DO NOTHING
        """)
        
        # Insertar platos de prueba
        cur.execute("""
        INSERT INTO platos (restaurante_id, nombre, descripcion, precio, categoria) VALUES
        (1, 'Churrasco', 'Corte de res a la parrilla', 25.99, 'Carnes'),
        (1, 'Costillas BBQ', 'Costillas de cerdo en salsa BBQ', 22.99, 'Carnes'),
        (2, 'Paella de Mariscos', 'Arroz con mariscos variados', 30.99, 'Mariscos'),
        (2, 'Ceviche', 'Ceviche de pescado fresco', 15.99, 'Entradas'),
        (3, 'Lasagna', 'Lasagna casera de carne', 18.99, 'Pasta'),
        (3, 'Spaghetti Carbonara', 'Pasta con salsa carbonara', 16.99, 'Pasta')
        ON CONFLICT DO NOTHING
        """)
        
        # Insertar algunas reservas de prueba
        cur.execute("""
        INSERT INTO reservas (cliente_nombre, cliente_email, cliente_telefono, restaurante_id, fecha_reserva, numero_personas) VALUES
        ('Juan Pérez', 'juan@email.com', '555-1111', 1, %s, 4),
        ('María García', 'maria@email.com', '555-2222', 2, %s, 2),
        ('Carlos López', 'carlos@email.com', '555-3333', 3, %s, 6)
        ON CONFLICT DO NOTHING
        """, (
            datetime.now() + timedelta(days=1),
            datetime.now() + timedelta(days=2),
            datetime.now() + timedelta(days=3)
        ))
        
        conn.commit()
        logger.info("Datos de prueba insertados exitosamente")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error insertando datos de prueba: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

def main():
    """Función principal de inicialización"""
    logger.info("Iniciando script de inicialización de la base de datos")
    
    if not wait_for_db():
        logger.error("No se pudo conectar a la base de datos. Abortando.")
        return False
    
    try:
        create_tables()
        insert_sample_data()
        logger.info("Inicialización completada exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error durante la inicialización: {str(e)}")
        return False

if __name__ == "__main__":
    main()