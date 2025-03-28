from pydantic import BaseModel, Field
from typing import Dict, Optional, Union
from uuid import UUID
from decimal import Decimal

class ProductBase(BaseModel):
    nombre: str
    precio: Decimal
    color: Optional[str] = None
    talla: Optional[str] = None
    caracteristicas: Dict = Field(default_factory=dict)
    disponible: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[Decimal] = None
    color: Optional[str] = None
    talla: Optional[str] = None
    caracteristicas: Optional[Dict] = None
    disponible: Optional[bool] = None

class ProductInDB(ProductBase):
    id: UUID
    foto: Optional[str] = None
    
    class Config:
        orm_mode = True

class ProductResponse(ProductInDB):
    pass

class ProductAvailability(BaseModel):
    disponible: bool