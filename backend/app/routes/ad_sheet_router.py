# app/routes/ad_sheet_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db import get_db
from app.schemas.ad_sheet import AdSheetResponse, AdSheetCreate, AdSheetUpdate
from app.crud import ad_sheet as ad_sheet_crud
from app.config import settings

router = APIRouter(tags=["ad_sheets"])

@router.get("/ad-sheets", response_model=List[AdSheetResponse])
async def get_ad_sheets(
    platform: Optional[str] = Query(None, description="Filtrar por plataforma"),
    db: Session = Depends(get_db)
):
    """Obtener todas las fichas publicitarias, opcionalmente filtradas por plataforma"""
    ad_sheets = ad_sheet_crud.get_ad_sheets(db, platform)
    return ad_sheets

@router.get("/ad-sheets/{ad_sheet_id}", response_model=AdSheetResponse)
async def get_ad_sheet(ad_sheet_id: UUID, db: Session = Depends(get_db)):
    """Obtener una ficha publicitaria por su ID"""
    db_ad_sheet = ad_sheet_crud.get_ad_sheet(db, ad_sheet_id)
    if db_ad_sheet is None:
        raise HTTPException(status_code=404, detail="Ficha publicitaria no encontrada")
    return db_ad_sheet

@router.post("/ad-sheets", response_model=AdSheetResponse, status_code=201)
async def create_ad_sheet(
    ad_sheet: AdSheetCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva ficha publicitaria"""
    try:
        # Validar que la plataforma y el template sean válidos
        if ad_sheet.platform not in settings.AD_TEMPLATES:
            raise HTTPException(
                status_code=400, 
                detail=f"Plataforma no válida. Opciones disponibles: {list(settings.AD_TEMPLATES.keys())}"
            )
            
        if ad_sheet.template not in settings.AD_TEMPLATES[ad_sheet.platform]:
            raise HTTPException(
                status_code=400, 
                detail=f"Template no válido para {ad_sheet.platform}. Opciones disponibles: {settings.AD_TEMPLATES[ad_sheet.platform]}"
            )
        
        return await ad_sheet_crud.create_ad_sheet(db, ad_sheet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la ficha publicitaria: {str(e)}")

@router.put("/ad-sheets/{ad_sheet_id}", response_model=AdSheetResponse)
async def update_ad_sheet(
    ad_sheet_id: UUID,
    ad_sheet: AdSheetUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una ficha publicitaria existente"""
    try:
        # Validar que la plataforma y el template sean válidos si se proporcionan
        if ad_sheet.platform is not None and ad_sheet.platform not in settings.AD_TEMPLATES:
            raise HTTPException(
                status_code=400, 
                detail=f"Plataforma no válida. Opciones disponibles: {list(settings.AD_TEMPLATES.keys())}"
            )
            
        if ad_sheet.platform is not None and ad_sheet.template is not None:
            if ad_sheet.template not in settings.AD_TEMPLATES[ad_sheet.platform]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Template no válido para {ad_sheet.platform}. Opciones disponibles: {settings.AD_TEMPLATES[ad_sheet.platform]}"
                )
        
        updated_ad_sheet = await ad_sheet_crud.update_ad_sheet(db, ad_sheet_id, ad_sheet)
        
        if updated_ad_sheet is None:
            raise HTTPException(status_code=404, detail="Ficha publicitaria no encontrada")
            
        return updated_ad_sheet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la ficha publicitaria: {str(e)}")

@router.delete("/ad-sheets/{ad_sheet_id}", status_code=200)
async def delete_ad_sheet(ad_sheet_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una ficha publicitaria"""
    deleted = ad_sheet_crud.delete_ad_sheet(db, ad_sheet_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Ficha publicitaria no encontrada")
    
    return {"message": "Ficha publicitaria eliminada con éxito"}

# Endpoint para obtener los templates disponibles
@router.get("/ad-templates")
async def get_available_templates():
    """Obtener los templates disponibles para cada plataforma"""
    return settings.AD_TEMPLATES