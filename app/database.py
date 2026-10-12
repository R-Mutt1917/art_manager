from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# El engine es la conexión a la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}, # Necesario para SQLite en Windows/Mac
    echo=False # Ponlo en True solo si quieres ver las queries SQL en consola para debug
)

def create_db_and_tables():
    """Crea todas las tablas definidas en los modelos."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency de FastAPI: provee una sesión de DB por request.
    Se cierra automáticamente al terminar el request.
    """
    with Session(engine) as session:
        yield session