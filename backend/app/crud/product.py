from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductAvailability
from app.utils.file_handlers import delete_file
import uuid

def get_product(db: Session, product_id: uuid.UUID):
    """Obtener un producto por su ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, disponible: Optional[bool] = None) -> List[Product]:
    """Obtener todos los productos, opcionalmente filtrados por disponibilidad"""
    query = db.query(Product)
    
    if disponible is not None:
        query = query.filter(Product.disponible == disponible)
        
    return query.all()

def create_product(db: Session, product: ProductCreate, foto: Optional[str] = None) -> Product:
    """Crear un nuevo producto"""
    # Convertir a diccionario y añadir foto si existe
    db_product = Product(
        **product.dict(),
        foto=foto
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

def update_product(
    db: Session, 
    product_id: uuid.UUID, 
    product: Union[ProductUpdate, Dict[str, Any]], 
    foto: Optional[str] = None
) -> Optional[Product]:
    """Actualizar un producto existente"""
    # Obtener producto existente
    db_product = get_product(db, product_id)
    
    if not db_product:
        return None
    
    # Actualizar campos
    update_data = product.dict(exclude_unset=True) if hasattr(product, 'dict') else product
    
    # Si hay nueva foto, eliminar la anterior
    if foto and db_product.foto:
        delete_file(db_product.foto)
    
    # Actualizar solo si hay nueva foto
    if foto:
        update_data["foto"] = foto
    
    # Aplicar actualizaciones
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product

def update_product_availability(
    db: Session, 
    product_id: uuid.UUID, 
    availability: ProductAvailability
) -> Optional[Product]:
    """Actualizar solo la disponibilidad de un producto"""
    return update_product(db, product_id, {"disponible": availability.disponible})

def delete_product(db: Session, product_id: uuid.UUID) -> bool:
    """Eliminar un producto"""
    db_product = get_product(db, product_id)
    
    if not db_product:
        return False
    
    # Eliminar la foto si existe
    if db_product.foto:
        delete_file(db_product.foto)
    
    db.delete(db_product)
    db.commit()
    
    return True