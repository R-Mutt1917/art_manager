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
    
    class Config:
        env_file = ".env"

# Instancia global para usar en toda la app
settings = Settings()

# Creamos la carpeta de uploads si no existe
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)