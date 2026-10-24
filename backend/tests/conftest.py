import pytest
import os
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import event
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
import app.models
from app.database import get_session

TEST_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_test_session():
    with Session(engine) as session:
        yield session

fastapi_app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(autouse=True)
def setup_database():
    """
    Destruye y recrea TODAS las tablas antes de cada test.
    Garantiza que el esquema esté siempre actualizado con los últimos modelos.
    """
    # 1. Borrar todo (incluye tablas con esquema viejo)
    SQLModel.metadata.drop_all(bind=engine)
    
    # 2. Recrear desde cero
    SQLModel.metadata.create_all(bind=engine)

    # Seed de datos iniciales
    with Session(engine) as session:
        from app.seed import seed_admin_user, seed_multitenancy
        seed_admin_user(session)
        seed_multitenancy(session)

    yield

    # Limpiar después de cada test
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    engine.dispose()
    if os.path.exists("./test_database.db"):
        try:
            os.remove("./test_database.db")
        except PermissionError:
            pass

@pytest.fixture
def client():
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def session():
    with Session(engine) as session:
        yield session

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Retorna headers de autorización para un usuario ADMIN con galería asignada."""
    r = client.post("/auth/register", json={
        "email": "test_admin@example.com",
        "nombre": "Test Admin",
        "password": "testpass123",
    })
    if r.status_code == 409:
        pass

    with Session(engine) as session:
        from app.models.usuario import Usuario, RolUsuario
        from app.models.galeria import Galeria
        
        usuario = session.exec(
            select(Usuario).where(Usuario.email == "test_admin@example.com")
        ).first()
        
        if usuario:
            # Asignar rol ADMIN
            usuario.rol = RolUsuario.ADMIN
            
            # ← NUEVO: Asignar Galería Demo al usuario de prueba
            galeria_demo = session.exec(
                select(Galeria).where(Galeria.slug == "galeria-demo")
            ).first()
            if galeria_demo:
                usuario.galeria_id = galeria_demo.id
            
            session.add(usuario)
            session.commit()

    r = client.post("/auth/login", json={
        "email": "test_admin@example.com",
        "password": "testpass123",
    })
    assert r.status_code == 200, r.json()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}