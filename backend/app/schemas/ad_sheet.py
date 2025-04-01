# app/schemas/ad_sheet.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime

class AdSheetBase(BaseModel):
    title: str
    platform: str
    template: str
    meta_info: Dict[str, Any] = Field(default_factory=dict)  # Cambiado de metadata a meta_info

class AdSheetCreate(AdSheetBase):
    product_ids: List[UUID]

class AdSheetUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    template: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None  # Cambiado de metadata a meta_info
    product_ids: Optional[List[UUID]] = None

class AdSheetInDB(AdSheetBase):
    id: UUID
    content: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class AdSheetResponse(AdSheetInDB):
    pass