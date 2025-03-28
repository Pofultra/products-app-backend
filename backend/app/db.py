from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear motor de SQLAlchemy
engine = create_engine(settings.DATABASE_URL)

# Clase base para los modelos
Base = declarative_base()

# Clase de sesión para las operaciones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()