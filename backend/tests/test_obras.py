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

def _crear_tecnica(client: TestClient, nombre: str | None = None) -> tuple[int, str]:
    """Crea una técnica y devuelve (id, nombre)."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
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


def _crear_obra(client: TestClient, tecnica_nombre: str, **overrides) -> dict:
    """Helper: crea una obra con FormData y devuelve el JSON de respuesta."""
    data = _form_obra(tecnica=tecnica_nombre)
    data.update(overrides)
    r = client.post("/obras/", data=data)
    assert r.status_code == 201, r.json()
    return r.json()


# ==========================================
# Tests de CREACIÓN
# ==========================================

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
        data=_form_obra(titulo="Obra con foto", tecnica=nombre),
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


# ==========================================
# Tests de LISTADO y DELETE
# ==========================================

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


# ==========================================
# Tests de ACTUALIZACIÓN (PUT)
# ==========================================

def test_actualizar_obra_conserva_imagen_si_no_se_envia_nueva(client: TestClient):
    """PUT actualiza campos y conserva la imagen si no se envía una nueva."""
    _, nombre = _crear_tecnica(client)

    # 1. Crear obra CON imagen
    r = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra original", tecnica=nombre),
        files={"imagen": ("foto.png", io.BytesIO(PNG_1x1), "image/png")},
    )
    assert r.status_code == 201, r.json()
    obra = r.json()
    imagen_original = obra["imagen_url"]
    assert imagen_original is not None

    # 2. Actualizar SIN enviar imagen (solo cambio de título y precio)
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
            # NO enviamos 'imagen'
        },
    )
    assert r_put.status_code == 200, r_put.json()
    actualizada = r_put.json()

    # 3. Verificar cambios aplicados
    assert actualizada["titulo"] == "Obra renombrada"
    assert actualizada["anio"] == 2025
    assert actualizada["precio"] == 9999.0

    # 4. Verificar que la imagen se CONSERVÓ
    assert actualizada["imagen_url"] == imagen_original

    # Cleanup del archivo físico
    ruta = Path("app") / imagen_original.lstrip("/")
    ruta.unlink(missing_ok=True)


def test_actualizar_obra_con_tecnica_nueva_la_crea(client: TestClient):
    """PUT con una técnica inexistente la crea y la asigna (upsert)."""
    _, nombre = _crear_tecnica(client)
    obra = client.post(
        "/obras/",
        data=_form_obra(titulo="Obra X", tecnica=nombre)
    ).json()

    tecnica_nueva = f"Técnica edición {uuid.uuid4().hex[:8]}"
    r_put = client.put(
        f"/obras/{obra['id']}",
        data=_form_obra(titulo="Obra X editada", tecnica=tecnica_nueva),
    )
    assert r_put.status_code == 200, r_put.json()

    # La técnica nueva debe existir ahora
    r_tec = client.get(f"/tecnicas/{r_put.json()['tecnica_id']}")
    assert r_tec.status_code == 200
    assert r_tec.json()["nombre"] == tecnica_nueva


def test_actualizar_obra_inexistente_devuelve_404(client: TestClient):
    """PUT a un ID que no existe debe devolver 404."""
    _, nombre = _crear_tecnica(client)
    r = client.put("/obras/99999", data=_form_obra(tecnica=nombre))
    assert r.status_code == 404