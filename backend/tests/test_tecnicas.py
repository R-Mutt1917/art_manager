"""
Tests del módulo de Técnicas.
Incluye el test crítico de GET /tecnicas/{id} que valida que el endpoint existe.
"""
import uuid
from fastapi.testclient import TestClient


def test_crear_y_obtener_tecnica_por_id(client: TestClient, auth_headers):
    """
    Test CRÍTICO: Crear una técnica y recuperarla individualmente por su ID.
    Este test confirmará si el endpoint GET /tecnicas/{id} está funcionando.
    """
    # 1. Crear una técnica (con auth)
    response_crear = client.post(
        "/tecnicas/",
        json={"nombre": "Óleo sobre lienzo", "descripcion": "Técnica clásica de prueba"},
        headers=auth_headers,
    )
    assert response_crear.status_code == 201, response_crear.json()
    tecnica_id = response_crear.json()["id"]

    # 2. Recuperar por ID (GET es público, no necesita auth)
    response_obtener = client.get(f"/tecnicas/{tecnica_id}")
    assert response_obtener.status_code == 200, response_obtener.json()

    # 3. Validar que los datos coincidan
    data = response_obtener.json()
    assert data["id"] == tecnica_id
    assert data["nombre"] == "Óleo sobre lienzo"
    assert data["descripcion"] == "Técnica clásica de prueba"


def test_listar_tecnicas(client: TestClient, auth_headers):
    """Test: Listar todas las técnicas."""
    # Crear una para asegurar que hay datos (con auth)
    r = client.post(
        "/tecnicas/", 
        json={"nombre": f"Acuarela {uuid.uuid4().hex[:8]}", "descripcion": "Agua"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()

    # GET es público
    response = client.get("/tecnicas/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ==========================================
# Tests de AUTORIZACIÓN (nuevos)
# ==========================================

def test_crear_tecnica_sin_token_devuelve_403(client: TestClient):
    """POST /tecnicas/ sin token debe devolver 403 (HTTPBearer estándar)."""
    r = client.post(
        "/tecnicas/",
        json={"nombre": "Técnica sin auth", "descripcion": "No debería crearse"},
    )
    assert r.status_code == 403


def test_crear_tecnica_con_rol_viewer_devuelve_403(client: TestClient):
    """POST /tecnicas/ con rol VIEWER debe devolver 403 (solo ADMIN/CURADOR)."""
    # Registrar un usuario VIEWER
    r = client.post("/auth/register", json={
        "email": "viewer_tec@example.com",
        "nombre": "Viewer Tec",
        "password": "viewer123",
    })
    assert r.status_code == 201

    # Login
    r = client.post("/auth/login", json={
        "email": "viewer_tec@example.com",
        "password": "viewer123",
    })
    viewer_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Intentar crear técnica (debe fallar con 403)
    r = client.post(
        "/tecnicas/",
        json={"nombre": "Técnica viewer", "descripcion": "No debería crearse"},
        headers=viewer_headers,
    )
    assert r.status_code == 403