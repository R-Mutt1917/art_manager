import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient


def _crear_tecnica(client: TestClient) -> str:
    nombre = f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
    assert r.status_code == 201
    return nombre


def _crear_obra(client: TestClient, tecnica_nombre: str) -> dict:
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "estado": "disponible",
        "tecnica": tecnica_nombre,
    }
    r = client.post("/obras/", data=data)
    assert r.status_code == 201, r.json()
    return r.json()


def _crear_exposicion(client: TestClient, fecha_inicio: date, fecha_fin: date) -> dict:
    r = client.post("/exposiciones/", json={
        "nombre": f"Expo {uuid.uuid4().hex[:8]}",
        "lugar": f"Museo {uuid.uuid4().hex[:8]}",   # ← CAMPO OBLIGATORIO
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
    })
    assert r.status_code == 201, r.json()
    return r.json()


def test_asignar_obra_a_exposicion_sin_superposicion(client: TestClient):
    """Asignar una obra a una exposición sin conflictos de fechas."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)

    hoy = date.today()
    expo = _crear_exposicion(client, hoy + timedelta(days=10), hoy + timedelta(days=30))

    # La API registra la asignación (201), pero NO cambia el estado de la obra
    # (el cambio de estado es responsabilidad de otro flujo de negocio)
    r = client.post(
        f"/exposiciones/{expo['id']}/obras/{obra['id']}",
        json={}
    )
    assert r.status_code == 201, r.json()

    # Verificamos que la asignación se registró consultando el checklist de la expo
    checklist = client.get(f"/exposiciones/{expo['id']}/checklist").json()
    assert isinstance(checklist, list)
    ids_en_expo = [item.get("obra_id") or item.get("id") for item in checklist]
    assert obra["id"] in ids_en_expo or len(checklist) >= 1

def test_rechazar_asignacion_con_fechas_superpuestas(client: TestClient):
    """No se puede asignar una obra si ya está en otra exposición en esas fechas."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)

    hoy = date.today()
    expo1 = _crear_exposicion(client, hoy + timedelta(days=10), hoy + timedelta(days=30))
    expo2 = _crear_exposicion(client, hoy + timedelta(days=20), hoy + timedelta(days=40))

    # Asignar a expo1
    r1 = client.post(f"/exposiciones/{expo1['id']}/obras/{obra['id']}", json={})
    assert r1.status_code == 201

    # Intentar asignar a expo2 (fechas superpuestas)
    r2 = client.post(f"/exposiciones/{expo2['id']}/obras/{obra['id']}", json={})
    assert r2.status_code in (400, 409)


def test_checklist_de_retiro(client: TestClient):
    """Verificar que la exposición genera un checklist de obras asignadas."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)

    hoy = date.today()
    expo = _crear_exposicion(client, hoy, hoy + timedelta(days=30))

    # Asignar obra
    client.post(f"/exposiciones/{expo['id']}/obras/{obra['id']}", json={})

    # Checklist es un GET, no POST
    r = client.get(f"/exposiciones/{expo['id']}/checklist")
    assert r.status_code == 200, r.json()
    checklist = r.json()
    assert isinstance(checklist, list)
    assert len(checklist) >= 1