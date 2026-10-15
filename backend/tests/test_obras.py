"""
Tests del módulo de Obras.
Contrato actual: POST /obras/ recibe multipart/form-data
"""
import io
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

PNG_1x1 = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01'
    b'\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


def _crear_tecnica(client: TestClient, nombre: str | None = None) -> tuple[int, str]:
    """Crea una técnica y devuelve (id, nombre)."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
    assert r.status_code == 201, r.json()
    return r.json()["id"], nombre


def _crear_obra(client: TestClient, tecnica_nombre: str, **overrides) -> dict:
    """Helper: crea una obra con FormData y devuelve el JSON de respuesta."""
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "precio": "1500",
        "estado": "disponible",
        "notas": "Nota de prueba",
        "tecnica": tecnica_nombre,  # ← Siempre incluir técnica
    }
    data.update(overrides)
    r = client.post("/obras/", data=data)
    assert r.status_code == 201, r.json()
    return r.json()


def test_crear_obra(client: TestClient):
    """Crear una obra con una técnica existente, sin imagen."""
    _, nombre = _crear_tecnica(client)
    data = _crear_obra(client, nombre, titulo="Atardecer en el Puerto")
    assert data["titulo"] == "Atardecer en el Puerto"
    assert data["precio"] == 1500.0


def test_crear_obra_con_imagen(client: TestClient):
    """Subir una imagen y verificar que se guarda y se vincula."""
    _, nombre = _crear_tecnica(client)
    
    r = client.post(
        "/obras/",
        data={
            "titulo": "Obra con foto",
            "anio": "2024",
            "dimensiones": "50x70 cm",
            "precio": "1500",
            "estado": "disponible",
            "tecnica": nombre,
        },
        files={"imagen": ("foto.png", io.BytesIO(PNG_1x1), "image/png")},
    )
    
    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["imagen_url"] is not None
    assert data["imagen_url"].startswith("/uploads/")
    
    ruta = Path("app") / data["imagen_url"].lstrip("/")
    assert ruta.exists()
    ruta.unlink(missing_ok=True)


def test_crear_obra_con_tecnica_inexistente_la_crea(client: TestClient):
    """Si la técnica no existe, se crea automáticamente."""
    nombre_unico = f"Técnica auto {uuid.uuid4().hex[:8]}"
    data = _crear_obra(client, nombre_unico, titulo="Obra nueva")
    
    r_tec = client.get(f"/tecnicas/{data['tecnica_id']}")
    assert r_tec.status_code == 200
    assert r_tec.json()["nombre"] == nombre_unico


def test_crear_obra_sin_tecnica_devuelve_422(client: TestClient):
    """El campo 'tecnica' es obligatorio."""
    payload = {
        "titulo": "Obra sin técnica",
        "anio": "2024",
        "dimensiones": "30x30 cm",
        # Falta 'tecnica' intencionalmente
    }
    r = client.post("/obras/", data=payload)
    assert r.status_code == 422


def test_listar_obras(client: TestClient):
    """Listar refleja las obras creadas."""
    _, nombre = _crear_tecnica(client)
    antes = len(client.get("/obras/").json())
    
    for i in range(2):
        _crear_obra(client, nombre, titulo=f"Obra {i}")
    
    despues = client.get("/obras/").json()
    assert len(despues) == antes + 2


def test_soft_delete(client: TestClient):
    """Eliminar una obra la oculta del listado y del GET por ID."""
    _, nombre = _crear_tecnica(client)
    obra = _crear_obra(client, nombre, titulo="Obra a eliminar")
    obra_id = obra["id"]
    
    r_delete = client.delete(f"/obras/{obra_id}")
    assert r_delete.status_code == 200, r_delete.json()
    assert "dada de baja" in r_delete.json()["mensaje"]
    
    ids = [o["id"] for o in client.get("/obras/").json()]
    assert obra_id not in ids
    
    assert client.get(f"/obras/{obra_id}").status_code == 404