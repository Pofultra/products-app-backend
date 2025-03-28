import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from PIL import Image
from app.config import settings

async def save_upload_file(file: UploadFile) -> str:
    """
    Guarda un archivo subido y devuelve el nombre del archivo guardado
    """
    # Validar que sea una imagen
    if not is_valid_image(file):
        raise HTTPException(status_code=400, detail="Formato de archivo no válido. Acepta solo JPG, JPEG, PNG o WEBP")

    # Generar nombre único
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Ruta de destino
    destination = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Crear archivo
    with open(destination, "wb") as buffer:
        # Copiar contenido
        shutil.copyfileobj(file.file, buffer)
    
    # Opcionalmente, se podría redimensionar o comprimir la imagen aquí
    try:
        # Abrir la imagen para verificar que es válida
        Image.open(destination)
    except Exception:
        # Si la imagen no es válida, eliminar el archivo y lanzar excepción
        os.remove(destination)
        raise HTTPException(status_code=400, detail="Archivo no es una imagen válida")
        
    return unique_filename

def delete_file(filename: str) -> bool:
    """
    Elimina un archivo del sistema de archivos
    """
    if not filename:
        return False
        
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    
    return False

def is_valid_image(file: UploadFile) -> bool:
    """
    Verifica si el archivo es una imagen válida basándose en la extensión
    """
    if not file.filename:
        return False
        
    # Obtener extensión y convertir a minúsculas
    ext = os.path.splitext(file.filename)[1].lower().replace(".", "")
    
    return ext in settings.ALLOWED_IMAGE_EXTENSIONS