from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from uuid import UUID

from app.db import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductAvailability
from app.crud import product as product_crud
from app.utils.file_handlers import save_upload_file

router = APIRouter(tags=["products"])

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    db: Session = Depends(get_db)
):
    """Obtener todos los productos, opcionalmente filtrados por disponibilidad"""
    products = product_crud.get_products(db, disponible)
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Obtener un producto por su ID"""
    db_product = product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_product

@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    nombre: str = Form(...),
    precio: float = Form(...),
    color: Optional[str] = Form(None),
    talla: Optional[str] = Form(None),
    caracteristicas: str = Form("{}"),
    disponible: bool = Form(True),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    # Procesar JSON de características
    try:
        caracteristicas_dict = json.loads(caracteristicas) if caracteristicas else {}
    except json.JSONDecodeError:
        caracteristicas_dict = {}
    
    # Crear objeto ProductCreate
    product_data = ProductCreate(
        nombre=nombre,
        precio=precio,
        color=color,
        talla=talla,
        caracteristicas=caracteristicas_dict,
        disponible=disponible
    )
    
    # Guardar imagen si existe
    foto_filename = None
    if foto:
        foto_filename = await save_upload_file(foto)
    
    # Crear producto en la base de datos
    return product_crud.create_product(db, product_data, foto_filename)

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    nombre: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    color: Optional[str] = Form(None),
    talla: Optional[str] = Form(None),
    caracteristicas: Optional[str] = Form(None),
    disponible: Optional[bool] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    # Verificar si el producto existe
    db_product = product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Preparar datos para actualización
    update_data = {}
    
    if nombre is not None:
        update_data["nombre"] = nombre
    
    if precio is not None:
        update_data["precio"] = precio
    
    if color is not None:
        update_data["color"] = color
    
    if talla is not None:
        update_data["talla"] = talla
    
    if caracteristicas is not None:
        try:
            update_data["caracteristicas"] = json.loads(caracteristicas)
        except json.JSONDecodeError:
            update_data["caracteristicas"] = {}
    
    if disponible is not None:
        update_data["disponible"] = disponible
    
    # Guardar imagen si existe
    foto_filename = None
    if foto:
        foto_filename = await save_upload_file(foto)
    
    # Actualizar producto
    updated_product = product_crud.update_product(db, product_id, update_data, foto_filename)
    
    if updated_product is None:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el producto")
    
    return updated_product

@router.patch("/products/{product_id}/availability", response_model=ProductResponse)
async def update_product_availability(
    product_id: UUID,
    availability: ProductAvailability,
    db: Session = Depends(get_db)
):
    """Actualizar solo la disponibilidad de un producto"""
    # Verificar si el producto existe
    db_product = product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizar disponibilidad
    updated_product = product_crud.update_product_availability(db, product_id, availability)
    
    if updated_product is None:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la disponibilidad")
    
    return updated_product

@router.delete("/products/{product_id}", status_code=200)
async def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un producto"""
    # Verificar si el producto existe
    db_product = product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Eliminar producto
    deleted = product_crud.delete_product(db, product_id)
    
    if not deleted:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el producto")
    
    return {"message": "Producto eliminado con éxito"}