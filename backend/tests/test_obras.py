"""
Tests del módulo de Obras.
Contrato actual: POST /obras/ recibe multipart/form-data
(campos de texto + archivo opcional 'imagen').
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
# Helpers (reducen duplicación entre tests)
# ==========================================

def _crear_tecnica(client: TestClient, nombre: str | None = None) -> tuple[int, str]:
    """Crea una técnica y devuelve (id, nombre)."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
    assert r.status_code == 201, r.json()
    return r.json()["id"], nombre


def _form_obra(**overrides) -> dict:
    """Devuelve un payload FormData válido para POST /obras/."""
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


# ==========================================
# 1. Creación básica (sin imagen)
# ==========================================

def test_crear_obra(client: TestClient):
    """Crear una obra con una técnica existente, sin imagen."""
    tecnica_id, nombre = _crear_tecnica(client)

    r = client.post("/obras/", data=_form_obra(titulo="Atardecer en el Puerto", tecnica=nombre))

    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["titulo"] == "Atardecer en el Puerto"
    assert data["precio"] == 1500.0
    assert data["tecnica_id"] == tecnica_id      # reutilizó la técnica existente
    assert data["imagen_url"] is None            # sin imagen → None


# ==========================================
# 2. Creación con imagen (flujo completo)
# ==========================================

def test_crear_obra_con_imagen(client: TestClient):
    """Subir una imagen y verificar que se guarda y se vincula a la obra."""
    _, nombre = _crear_tecnica(client)

    r = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra con foto", tecnica=nombre),
        files={"imagen": ("foto.png", io.BytesIO(PNG_1x1), "image/png")},
    )

    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["imagen_url"] is not None
    assert data["imagen_url"].startswith("/uploads/")
    assert data["imagen_url"].endswith(".png")

    # El archivo debe existir físicamente en disco
    ruta = Path("app") / data["imagen_url"].lstrip("/")
    assert ruta.exists(), f"No se guardó el archivo en {ruta}"
    ruta.unlink(missing_ok=True)  # cleanup


# ==========================================
# 3. Auto-creación de técnica (upsert)
# ==========================================

def test_crear_obra_con_tecnica_inexistente_la_crea(client: TestClient):
    """Si la técnica no existe, se crea automáticamente y se vincula."""
    nombre_unico = f"Técnica auto {uuid.uuid4().hex[:8]}"

    r = client.post("/obras/", data=_form_obra(titulo="Obra nueva", tecnica=nombre_unico))

    assert r.status_code == 201, r.json()
    obra = r.json()

    r_tec = client.get(f"/tecnicas/{obra['tecnica_id']}")
    assert r_tec.status_code == 200
    assert r_tec.json()["nombre"] == nombre_unico


# ==========================================
# 4. Validaciones
# ==========================================

def test_crear_obra_sin_tecnica_devuelve_422(client: TestClient):
    """El campo 'tecnica' es obligatorio."""
    payload = _form_obra()
    payload.pop("tecnica")

    r = client.post("/obras/", data=payload)
    assert r.status_code == 422


# ==========================================
# 5. Listado
# ==========================================

def test_listar_obras(client: TestClient):
    """Listar refleja las obras creadas (usamos delta para ser robustos)."""
    _, nombre = _crear_tecnica(client)
    antes = len(client.get("/obras/").json())

    for i in range(2):
        r = client.post("/obras/", data=_form_obra(titulo=f"Obra {i}", tecnica=nombre))
        assert r.status_code == 201

    despues = client.get("/obras/").json()
    assert len(despues) == antes + 2


# ==========================================
# 6. Soft delete
# ==========================================

def test_soft_delete(client: TestClient):
    """Eliminar una obra la oculta del listado y del GET por ID, sin borrarla de la BD."""
    _, nombre = _crear_tecnica(client)
    obra_id = client.post("/obras/", data=_form_obra(titulo="Obra a eliminar", tecnica=nombre)).json()["id"]

    r_delete = client.delete(f"/obras/{obra_id}")
    assert r_delete.status_code == 200
    assert "dada de baja" in r_delete.json()["mensaje"]

    # Ya no aparece en el listado
    ids = [o["id"] for o in client.get("/obras/").json()]
    assert obra_id not in ids

    # GET por ID → 404
    assert client.get(f"/obras/{obra_id}").status_code == 404