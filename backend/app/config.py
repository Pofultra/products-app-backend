from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    # Configuraciones existentes...
    
    # Configuración del LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" o "anthropic"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Templates disponibles
    AD_TEMPLATES: dict = {
        "facebook": ["basic", "detailed"],
        "whatsapp": ["basic", "detailed"],
        "revolico": ["basic", "detailed"]
    }
    
    # Configuración de la base de datos
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "productos_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    
    # URL de conexión a la base de datos
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Directorio de uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Tamaño máximo de imágenes
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Configuración de la aplicación
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    
    # Extensiones de imagen permitidas
    ALLOWED_IMAGE_EXTENSIONS: list = ["jpg", "jpeg", "png", "webp"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instanciar configuración
settings = Settings()