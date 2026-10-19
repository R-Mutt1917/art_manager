import pytest
import os
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

# 1. Importamos la app y los modelos
from app.main import app as fastapi_app
import app.models
from app.database import get_session

# 2. Usamos un ARCHIVO REAL temporal para los tests (mucho más estable que sqlite:// en memoria)
TEST_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 3. Dependencia de prueba
def get_test_session():
    with Session(engine) as session:
        yield session

# 4. Sobreescribimos la dependencia de sesión
fastapi_app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(autouse=True)
def setup_database():
    """
    Crea las tablas en el archivo de prueba ANTES de cada test,
    siembra datos iniciales necesarios (admin) y las borra DESPUÉS.
    
    Esto garantiza que cada test empieza con el mismo estado predecible.
    """
    SQLModel.metadata.create_all(bind=engine)
    
    # Seed de datos iniciales necesarios para tests
    with Session(engine) as session:
        from app.seed import seed_admin_user
        seed_admin_user(session)
    
    yield
    
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """
    Elimina el archivo de base de datos de prueba al finalizar 
    TODA la ejecución de pytest, pero primero libera el bloqueo de Windows.
    """
    yield
    # 1. Cerrar todas las conexiones activas para liberar el archivo
    engine.dispose()
    
    # 2. Ahora sí, Windows nos dejará borrarlo
    if os.path.exists("./test_database.db"):
        try:
            os.remove("./test_database.db")
        except PermissionError:
            # Si por alguna razón sigue bloqueado, no interrumpimos el reporte de tests
            pass 

@pytest.fixture
def client():
    """Cliente de prueba."""
    with TestClient(fastapi_app) as c:
        yield c