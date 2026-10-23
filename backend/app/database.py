from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import settings

# El engine es la conexión a la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False,  # Ponlo en True solo si quieres ver las queries SQL en consola para debug
)

# ==========================================
# ACTIVAR FOREIGN KEYS EN SQLITE
# ==========================================
# SQLite NO valida foreign keys por defecto (decisión histórica de SQLite
# para compatibilidad con BDs viejas). Este listener ejecuta
# "PRAGMA foreign_keys=ON" cada vez que se abre una conexión, garantizando
# integridad referencial. En producción (PostgreSQL) esto no es necesario.
#
# Esto es CRÍTICO para el multi-tenancy: sin esta validación, una obra
# podría guardarse con un galeria_id inexistente y romper el aislamiento.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Activa validación de FKs en cada conexión SQLite."""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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