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
    
    r = client.post(f"/exposiciones/{expo['id']}/asignar/{obra['id']}")
    assert r.status_code == 200, r.json()
    
    # Verificar que la obra está en exposición
    obra_actualizada = client.get(f"/obras/{obra['id']}").json()
    assert obra_actualizada["estado"] == "en_exposicion"


def test_rechazar_asignacion_con_fechas_superpuestas(client: TestClient):
    """No se puede asignar una obra si ya está en otra exposición en esas fechas."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    
    hoy = date.today()
    expo1 = _crear_exposicion(client, hoy + timedelta(days=10), hoy + timedelta(days=30))
    expo2 = _crear_exposicion(client, hoy + timedelta(days=20), hoy + timedelta(days=40))
    
    # Asignar a expo1
    r1 = client.post(f"/exposiciones/{expo1['id']}/asignar/{obra['id']}")
    assert r1.status_code == 200
    
    # Intentar asignar a expo2 (fechas superpuestas)
    r2 = client.post(f"/exposiciones/{expo2['id']}/asignar/{obra['id']}")
    assert r2.status_code == 400
    assert "conflicto" in r2.json()["detail"].lower()


def test_checklist_de_retiro(client: TestClient):
    """Marcar el checklist de retiro de una obra en exposición."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    
    hoy = date.today()
    expo = _crear_exposicion(client, hoy, hoy + timedelta(days=30))
    
    # Asignar obra
    client.post(f"/exposiciones/{expo['id']}/asignar/{obra['id']}")
    
    # Marcar checklist
    r = client.post(f"/exposiciones/{expo['id']}/obras/{obra['id']}/checklist-retiro", json={
        "estado_embalaje": "excelente",
        "condiciones_transporte": "aprobado",
        "documentacion_completa": True,
    })
    assert r.status_code == 200, r.json()
    assert r.json()["checklist_retiro_completado"] is True