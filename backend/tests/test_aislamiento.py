import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.models.galeria import Galeria
from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
from app.models.obra import Obra
from app.core.security import hash_password

@pytest.fixture
def setup_multi_tenant_test(session: Session):
    """Crea 2 galerías y 2 usuarios con roles aislados para testing."""
    # 1. Crear Galerías
    galeria_a = Galeria(nombre="Galería A", slug="galeria-a", activo=True)
    galeria_b = Galeria(nombre="Galería B", slug="galeria-b", activo=True)
    session.add(galeria_a)
    session.add(galeria_b)
    session.commit()
    session.refresh(galeria_a)
    session.refresh(galeria_b)

    # 2. Crear Usuarios (UserAccount)
    user_a = UserAccount(
        email="admin@galeria-a.com",
        nombre="Admin A",
        password_hash=hash_password("password123"),
        galeria_id_activa=galeria_a.id
    )
    user_b = UserAccount(
        email="admin@galeria-b.com",
        nombre="Admin B",
        password_hash=hash_password("password123"),
        galeria_id_activa=galeria_b.id
    )
    session.add(user_a)
    session.add(user_b)
    session.commit()
    session.refresh(user_a)
    session.refresh(user_b)

    # 3. Asignar Roles (UserGalleryRole)
    role_a = UserGalleryRole(user_id=user_a.id, galeria_id=galeria_a.id, rol=RolUsuario.ADMIN)
    role_b = UserGalleryRole(user_id=user_b.id, galeria_id=galeria_b.id, rol=RolUsuario.ADMIN)
    session.add(role_a)
    session.add(role_b)
    session.commit()

    # 4. Crear una obra de prueba en cada galería (con campos obligatorios)
    obra_a = Obra(
        titulo="Obra de A", 
        anio=2024,
        dimensiones="100x100 cm",
        galeria_id=galeria_a.id, 
        estado="disponible"
    )
    obra_b = Obra(
        titulo="Obra de B", 
        anio=2024,
        dimensiones="100x100 cm",
        galeria_id=galeria_b.id, 
        estado="disponible"
    )
    session.add(obra_a)
    session.add(obra_b)
    session.commit()
    session.refresh(obra_a)
    session.refresh(obra_b)

    return {
        "galeria_a": galeria_a,
        "galeria_b": galeria_b,
        "user_a": user_a,
        "user_b": user_b,
        "obra_a": obra_a,
        "obra_b": obra_b
    }

def test_aislamiento_lectura_obras(client: TestClient, session: Session, setup_multi_tenant_test):
    """El usuario de la Galería A NO debe poder ver las obras de la Galería B."""
    data = setup_multi_tenant_test
    
    # 1. Simular login del usuario A
    login_response = client.post("/auth/login", json={
        "email": "admin@galeria-a.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Intentar obtener la obra de la Galería B
    response = client.get(f"/obras/{data['obra_b'].id}", headers=headers)
    
    # 3. Debe fallar con 404 (No encontrado) o 403 (Prohibido), pero NUNCA 200.
    assert response.status_code in [403, 404], f"¡Fallo de aislamiento! Esperaba 403 o 404, pero obtuvo {response.status_code}"

def test_aislamiento_escritura_obras(client: TestClient, session: Session, setup_multi_tenant_test):
    """El usuario de la Galería A NO debe poder editar una obra de la Galería B."""
    data = setup_multi_tenant_test
    
    # 1. Login del usuario A
    login_response = client.post("/auth/login", json={
        "email": "admin@galeria-a.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Intentar editar la obra de la Galería B con un payload lo más válido posible
    files = {"imagen": ("test.jpg", b"fake image data", "image/jpeg")}
    data_payload = {
        "titulo": "Obra de B hackeada", 
        "anio": 2024, 
        "dimensiones": "100x100 cm",
        "estado": "disponible",
        "precio": 1000
    }
    
    response = client.put(f"/obras/{data['obra_b'].id}", headers=headers, files=files, data=data_payload)
    
    # 3. La petición DEBE ser rechazada (403 Forbidden, 404 Not Found, o 422 si falta algún campo del schema).
    # Lo CRÍTICO es que NUNCA sea 200 OK.
    assert response.status_code != 200, f"¡Fallo de aislamiento CRÍTICO! La obra fue editada exitosamente (Status {response.status_code})"
    
    # 4. Verificación definitiva: la obra B no fue modificada en la Base de Datos
    session.refresh(data['obra_b'])
    assert data['obra_b'].titulo == "Obra de B", "¡CRÍTICO! La obra fue modificada ilegalmente por otro tenant."