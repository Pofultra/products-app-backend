from sqlalchemy import Column, String, Numeric, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    color = Column(String, nullable=True)
    talla = Column(String, nullable=True)
    caracteristicas = Column(JSON, nullable=True, default={})
    foto = Column(String, nullable=True)
    disponible = Column(Boolean, nullable=False, default=True)