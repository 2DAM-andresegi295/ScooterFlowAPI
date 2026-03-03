import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"  # archivo SQLite local

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # requerido por SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dependencia de FastAPI para inyectar la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''


# 1. Obtener la URL de la base de datos desde una variable de entorno
# En Render, ellos te dan esta URL.
# En local, puedes poner una por defecto o usar un archivo .env
# Obtenemos la URL de la variable de entorno
load_dotenv()

uri = os.getenv('DATABASE_URL')

# FIX: SQLAlchemy requiere "postgresql://" en lugar de "postgres://"
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

DATABASE_URL = uri

# 2. Configuración del Engine
# Nota: Eliminamos 'connect_args' porque era específico para SQLite
engine = create_engine(DATABASE_URL)

# 3. Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase Base para los modelos
class Base(DeclarativeBase):
    pass

# 5. Dependencia para inyectar la sesión en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()