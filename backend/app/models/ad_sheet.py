# app/models/ad_sheet.py
from sqlalchemy import Column, String, JSON, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base

# Tabla de asociación para la relación muchos a muchos entre fichas y productos
ad_sheet_product = Table(
    'ad_sheet_product',
    Base.metadata,
    Column('ad_sheet_id', UUID(as_uuid=True), ForeignKey('ad_sheets.id')),
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'))
)

class AdSheet(Base):
    __tablename__ = "ad_sheets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # "facebook", "whatsapp", "revolico", etc.
    template = Column(String, nullable=False)  # Nombre del template utilizado
    content = Column(String, nullable=False)  # Contenido en markdown
    meta_info = Column(JSON, nullable=True, default={}) # Metadatos adicionales
    
    # Relación muchos a muchos con productos
    products = relationship("Product", secondary=ad_sheet_product, backref="ad_sheets")