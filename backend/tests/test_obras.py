"""
Tests del módulo de Obras.
Contrato actual: POST y PUT /obras/ reciben multipart/form-data
"""
import io
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

# PNG mínimo válido (1x1 px) para pruebas de subida
PNG_1x1 = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01'
    b'\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)

# ==========================================
# Helpers
# ==========================================

def _crear_tecnica(client: TestClient, nombre: str | None = None, headers: dict = None) -> tuple[int, str]:
    """Crea una técnica y devuelve (id, nombre)."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"}, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()["id"], nombre

def _form_obra(**overrides) -> dict:
    """Devuelve un payload FormData válido para POST/PUT /obras/."""
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "precio": "1500",
        "estado": "disponible",
        "notas": "Nota de prueba",
    }
    data.update(overrides)
    return data

def _crear_obra(client: TestClient, tecnica_nombre: str, headers: dict = None, **overrides) -> dict:
    """Helper: crea una obra con FormData y devuelve el JSON de respuesta."""
    data = _form_obra(tecnica=tecnica_nombre)
    data.update(overrides)
    r = client.post("/obras/", data=data, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()

# ==========================================
# Tests de CREACIÓN
# ==========================================

def test_crear_obra(client: TestClient, auth_headers):
    """Crear una obra con una técnica existente, sin imagen."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)
    data = _crear_obra(client, nombre, headers=auth_headers, titulo="Atardecer en el Puerto")
    assert data["titulo"] == "Atardecer en el Puerto"
    assert data["precio"] == 1500.0

def test_crear_obra_con_imagen(client: TestClient, auth_headers: dict):
    """Subir una imagen y verificar que se guarda y se vincula."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)

    r = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra con foto", tecnica=nombre),
        files={"imagen": ("foto.png", io.BytesIO(PNG_1x1), "image/png")},
        headers=auth_headers
    )

    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["imagen_url"] is not None
    assert data["imagen_url"].startswith("/uploads/")

    ruta = Path("app") / data["imagen_url"].lstrip("/")
    assert ruta.exists()
    ruta.unlink(missing_ok=True)

def test_crear_obra_con_tecnica_inexistente_la_crea(client: TestClient, auth_headers):
    """Si la técnica no existe, se crea automáticamente."""
    nombre_unico = f"Técnica auto {uuid.uuid4().hex[:8]}"
    data = _crear_obra(client, nombre_unico, headers=auth_headers, titulo="Obra nueva")

    r_tec = client.get(f"/tecnicas/{data['tecnica_id']}")
    assert r_tec.status_code == 200
    assert r_tec.json()["nombre"] == nombre_unico

def test_crear_obra_sin_tecnica_devuelve_422(client: TestClient, auth_headers):
    """El campo 'tecnica' es obligatorio."""
    payload = {
        "titulo": "Obra sin técnica",
        "anio": "2024",
        "dimensiones": "30x30 cm",
    }
    r = client.post("/obras/", data=payload, headers=auth_headers)
    assert r.status_code == 422

# ==========================================
# Tests de LISTADO y DELETE
# ==========================================

def test_listar_obras(client: TestClient, auth_headers):
    """Listar refleja las obras creadas."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)
    antes = len(client.get("/obras/", headers=auth_headers).json())  # ← agregar headers

    for i in range(2):
        _crear_obra(client, nombre, headers=auth_headers, titulo=f"Obra {i}")

    despues = client.get("/obras/", headers=auth_headers).json()  # ← agregar headers
    assert len(despues) == antes + 2

def test_soft_delete(client: TestClient, auth_headers):
    """Eliminar una obra la oculta del listado y del GET por ID."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre, headers=auth_headers, titulo="Obra a eliminar")
    obra_id = obra["id"]

    r_delete = client.delete(f"/obras/{obra_id}", headers=auth_headers)
    assert r_delete.status_code == 200, r_delete.json()
    assert "dada de baja" in r_delete.json()["mensaje"]

    ids = [o["id"] for o in client.get("/obras/", headers=auth_headers).json()]  # ← agregar headers
    assert obra_id not in ids

    r_get = client.get(f"/obras/{obra_id}", headers=auth_headers)  # ← agregar headers
    assert r_get.status_code == 404

# ==========================================
# Tests de ACTUALIZACIÓN (PUT)
# ==========================================

def test_actualizar_obra_conserva_imagen_si_no_se_envia_nueva(client: TestClient, auth_headers):
    """PUT actualiza campos y conserva la imagen si no se envía una nueva."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)

    r = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra original", tecnica=nombre),
        files={"imagen": ("foto.png", io.BytesIO(PNG_1x1), "image/png")},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()
    obra = r.json()
    imagen_original = obra["imagen_url"]
    assert imagen_original is not None

    r_put = client.put(
        f"/obras/{obra['id']}",
        data={
            "titulo": "Obra renombrada",
            "anio": "2025",
            "dimensiones": "60x60 cm",
            "precio": "9999",
            "estado": "disponible",
            "notas": "Editada",
            "tecnica": nombre,
        },
        headers=auth_headers,
    )
    assert r_put.status_code == 200, r_put.json()
    actualizada = r_put.json()

    assert actualizada["titulo"] == "Obra renombrada"
    assert actualizada["anio"] == 2025
    assert actualizada["precio"] == 9999.0
    assert actualizada["imagen_url"] == imagen_original

    ruta = Path("app") / imagen_original.lstrip("/")
    ruta.unlink(missing_ok=True)

def test_actualizar_obra_con_tecnica_nueva_la_crea(client: TestClient, auth_headers):
    """PUT con una técnica inexistente la crea y la asigna (upsert)."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)
    obra = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra X", tecnica=nombre),
        headers=auth_headers,
    ).json()

    tecnica_nueva = f"Técnica edición {uuid.uuid4().hex[:8]}"
    r_put = client.put(
        f"/obras/{obra['id']}",
        data=_form_obra(titulo="Obra X editada", tecnica=tecnica_nueva),
        headers=auth_headers,
    )
    assert r_put.status_code == 200, r_put.json()

    r_tec = client.get(f"/tecnicas/{r_put.json()['tecnica_id']}")
    assert r_tec.status_code == 200
    assert r_tec.json()["nombre"] == tecnica_nueva

def test_actualizar_obra_inexistente_devuelve_404(client: TestClient, auth_headers):
    """PUT a un ID que no existe debe devolver 404."""
    _, nombre = _crear_tecnica(client, headers=auth_headers)
    r = client.put("/obras/99999", data=_form_obra(tecnica=nombre), headers=auth_headers)
    assert r.status_code == 404

# ==========================================
# Tests de AUTORIZACIÓN (nuevos)
# ==========================================

def test_crear_obra_sin_token_devuelve_401(client: TestClient):
    """POST sin token de autenticación debe devolver 403 (HTTPBearer estándar)."""
    _, nombre = _crear_tecnica(client, headers=_get_admin_headers(client))
    r = client.post("/obras/", data=_form_obra(tecnica=nombre))
    assert r.status_code == 403

def test_crear_obra_con_rol_viewer_devuelve_403(client: TestClient):
    """POST con rol VIEWER (solo lectura) debe devolver 403."""
    r = client.post("/auth/register", json={
        "email": "viewer@example.com",
        "nombre": "Viewer",
        "password": "viewer123",
    })
    assert r.status_code == 201

    r = client.post("/auth/login", json={
        "email": "viewer@example.com",
        "password": "viewer123",
    })
    assert r.status_code == 200
    viewer_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    _, nombre = _crear_tecnica(client, headers=_get_admin_headers(client))
    r = client.post("/obras/", data=_form_obra(tecnica=nombre), headers=viewer_headers)
    assert r.status_code == 403

def _get_admin_headers(client: TestClient) -> dict:
    """Helper para obtener headers de admin en tests."""
    r = client.post("/auth/login", json={
        "email": "admin@artmanager.com",
        "password": "admin123",
    })
    return {"Authorization": f"Bearer {r.json()['access_token']}"}