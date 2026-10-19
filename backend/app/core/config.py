from pathlib import Path
from pydantic_settings import BaseSettings

# Obtenemos la ruta raíz del proyecto (dos niveles arriba de este archivo)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configuración global de la aplicación."""
    
    # Base de datos: SQLite en la raíz del proyecto
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/database.db"
    
    # Carpeta donde se guardarán las imágenes subidas
    UPLOAD_DIR: Path = BASE_DIR / "app" / "uploads"
    
    # Tamaño máximo de imagen: 5 MB
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    
    # Modo depuración (para ver mensajes en consola)
    DEBUG: bool = True

    # ==========================================
    # AUTENTICACIÓN (Fase 2)
    # ==========================================
    # ⚠️ En producción, sobreescribir con variable de entorno fuerte (min 32 chars)
    SECRET_KEY: str = "dev-secret-key-CAMBIAR-EN-PRODUCCION-usa-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"


# Instancia global para usar en toda la app
settings = Settings()

# Creamos la carpeta de uploads si no existe
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)