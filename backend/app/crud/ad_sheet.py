# app/crud/ad_sheet.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import datetime

from app.models.ad_sheet import AdSheet
from app.models.product import Product
from app.schemas.ad_sheet import AdSheetCreate, AdSheetUpdate
from app.utils.llm_generator import generate_ad_sheet_content

def get_ad_sheet(db: Session, ad_sheet_id: UUID):
    """Obtener una ficha publicitaria por su ID"""
    return db.query(AdSheet).filter(AdSheet.id == ad_sheet_id).first()

def get_ad_sheets(db: Session, platform: Optional[str] = None) -> List[AdSheet]:
    """Obtener todas las fichas publicitarias, opcionalmente filtradas por plataforma"""
    query = db.query(AdSheet)
    
    if platform:
        query = query.filter(AdSheet.platform == platform)
        
    return query.all()

def create_ad_sheet(db: Session, ad_sheet: AdSheetCreate) -> AdSheet:
    """Crear una nueva ficha publicitaria"""
    # Obtener los productos relacionados
    products = db.query(Product).filter(Product.id.in_(ad_sheet.product_ids)).all()
    
    if not products:
        raise ValueError("No se encontraron productos con los IDs proporcionados")
    
    # Generar el contenido de la ficha usando el generador LLM
    content = generate_ad_sheet_content(products, ad_sheet.platform, ad_sheet.template)
    
    # Crear la ficha publicitaria
    db_ad_sheet = AdSheet(
    title=ad_sheet.title,
    platform=ad_sheet.platform,
    template=ad_sheet.template,
    content=content,
    meta_info=ad_sheet.meta_info,
    products=products
)
    
    db.add(db_ad_sheet)
    db.commit()
    db.refresh(db_ad_sheet)
    
    return db_ad_sheet

def update_ad_sheet(db: Session, ad_sheet_id: UUID, ad_sheet: AdSheetUpdate) -> Optional[AdSheet]:
    """Actualizar una ficha publicitaria existente"""
    db_ad_sheet = get_ad_sheet(db, ad_sheet_id)
    
    if not db_ad_sheet:
        return None
    
    # Actualizar campos básicos
    if ad_sheet.title is not None:
        db_ad_sheet.title = ad_sheet.title
    
    if ad_sheet.platform is not None:
        db_ad_sheet.platform = ad_sheet.platform
    
    if ad_sheet.template is not None:
        db_ad_sheet.template = ad_sheet.template
    
    if ad_sheet.meta_info is not None:
        db_ad_sheet.meta_info = ad_sheet.meta_info
    
    # Actualizar productos relacionados si se proporcionaron
    if ad_sheet.product_ids is not None:
        products = db.query(Product).filter(Product.id.in_(ad_sheet.product_ids)).all()
        
        if not products:
            raise ValueError("No se encontraron productos con los IDs proporcionados")
        
        db_ad_sheet.products = products
        
        # Regenerar el contenido de la ficha
        db_ad_sheet.content = generate_ad_sheet_content(products, db_ad_sheet.platform, db_ad_sheet.template)
    
    db.commit()
    db.refresh(db_ad_sheet)
    
    return db_ad_sheet

def delete_ad_sheet(db: Session, ad_sheet_id: UUID) -> bool:
    """Eliminar una ficha publicitaria"""
    db_ad_sheet = get_ad_sheet(db, ad_sheet_id)
    
    if not db_ad_sheet:
        return False
    
    db.delete(db_ad_sheet)
    db.commit()
    
    return True