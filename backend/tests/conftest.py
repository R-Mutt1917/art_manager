import pytest
import os
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import event
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

# ==========================================
# ACTIVAR FOREIGN KEYS EN SQLITE (TESTS)
# ==========================================
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
    siembra datos iniciales necesarios y las borra DESPUÉS.
    """
    SQLModel.metadata.create_all(bind=engine)

    # Seed de datos iniciales (una sola llamada, idempotente)
    with Session(engine) as session:
        from app.seed import seed_admin_user, seed_multitenancy
        seed_admin_user(session)
        seed_multitenancy(session)

    yield

    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Elimina el archivo de BD de prueba al finalizar toda la ejecución de pytest."""
    yield
    engine.dispose()
    if os.path.exists("./test_database.db"):
        try:
            os.remove("./test_database.db")
        except PermissionError:
            pass

@pytest.fixture
def client():
    """Cliente de prueba."""
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def session():
    """Sesión de BD directa para tests de modelo (sin HTTP)."""
    with Session(engine) as session:
        yield session

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Retorna headers de autorización para un usuario ADMIN."""
    r = client.post("/auth/register", json={
        "email": "test_admin@example.com",
        "nombre": "Test Admin",
        "password": "testpass123",
    })
    if r.status_code == 409:
        pass

    with Session(engine) as session:
        from app.models.usuario import Usuario, RolUsuario
        usuario = session.exec(
            select(Usuario).where(Usuario.email == "test_admin@example.com")
        ).first()
        if usuario:
            usuario.rol = RolUsuario.ADMIN
            session.add(usuario)
            session.commit()

    r = client.post("/auth/login", json={
        "email": "test_admin@example.com",
        "password": "testpass123",
    })
    assert r.status_code == 200, r.json()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}