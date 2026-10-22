import pytest
import os
from sqlmodel import SQLModel, Session, create_engine, select
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

@pytest.fixture
def session():
    """
    Sesión de BD directa para tests de modelo (sin HTTP).
    Útil para tests unitarios de lógica de dominio que no necesitan
    pasar por los endpoints.
    
    Las tablas ya están creadas por setup_database (autouse=True).
    """
    with Session(engine) as session:
        yield session

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """
    Retorna headers de autorización para un usuario ADMIN.
    Uso: client.post("/obras/", data=..., headers=auth_headers)
    """
    # Registrar un usuario admin para tests
    r = client.post("/auth/register", json={
        "email": "test_admin@example.com",
        "nombre": "Test Admin",
        "password": "testpass123",
    })
    
    # Si ya existe (409), ignorar
    if r.status_code == 409:
        pass
    
    # Actualizar rol a ADMIN directamente en la BD (porque register siempre crea VIEWER)
    with Session(engine) as session:
        from app.models.usuario import Usuario, RolUsuario
        usuario = session.exec(
            select(Usuario).where(Usuario.email == "test_admin@example.com")
        ).first()
        if usuario:
            usuario.rol = RolUsuario.ADMIN
            session.add(usuario)
            session.commit()
    
    # Login para obtener token
    r = client.post("/auth/login", json={
        "email": "test_admin@example.com",
        "password": "testpass123",
    })
    assert r.status_code == 200, r.json()
    
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}