from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.config import settings
from app.routes import product_router, ad_sheet_router
from app.db import Base, engine  # Importamos Base y engine para crear las tablas

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear directorios si no existen
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Productos",
    description="API para gestionar productos con operaciones CRUD completas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limita a los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para las imágenes subidas
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Incluir rutas
app.include_router(product_router.router, prefix="/api")
app.include_router(ad_sheet_router.router, prefix="/api")
# Ruta de health check
@app.get("/health")
async def health_check():
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)