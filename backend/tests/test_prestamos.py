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


def _crear_prestamo(client: TestClient, obra_id: int, fecha_inicio: date, fecha_fin: date) -> dict:
    r = client.post("/prestamos/", json={
        "obra_id": obra_id,
        "institucion_destino": f"Museo {uuid.uuid4().hex[:8]}",
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "motivo": "Exposición temporal",
    })
    assert r.status_code == 201, r.json()
    return r.json()


def test_ciclo_completo_de_prestamo(client: TestClient):
    """Crear préstamo, confirmar salida, y registrar devolución."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    
    hoy = date.today()
    prestamo = _crear_prestamo(client, obra["id"], hoy, hoy + timedelta(days=30))
    
    # Confirmar salida
    r_salida = client.post(f"/prestamos/{prestamo['id']}/confirmar-salida")
    assert r_salida.status_code == 200, r_salida.json()
    
    obra_actualizada = client.get(f"/obras/{obra['id']}").json()
    assert obra_actualizada["estado"] == "en_prestamo"
    
    # Registrar devolución
    r_dev = client.post(f"/prestamos/{prestamo['id']}/registrar-devolucion", json={
        "condicion_retorno": "excelente",
        "observaciones": "Sin daños"
    })
    assert r_dev.status_code == 200, r_dev.json()
    
    obra_final = client.get(f"/obras/{obra['id']}").json()
    assert obra_final["estado"] == "disponible"


def test_no_se_puede_prestar_una_obra_vendida(client: TestClient):
    """Una obra vendida no puede ser prestada."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    
    # Vender la obra primero
    comprador = client.post("/compradores/", json={
        "nombre": "Comprador Test",
        "email": "test@example.com"
    }).json()
    
    client.post(f"/compradores/{comprador['id']}/comprar/{obra['id']}")
    
    # Intentar crear préstamo
    hoy = date.today()
    r = client.post("/prestamos/", json={
        "obra_id": obra["id"],
        "institucion_destino": "Museo Test",
        "fecha_inicio": hoy.isoformat(),
        "fecha_fin": (hoy + timedelta(days=30)).isoformat(),
        "motivo": "Préstamo",
    })
    assert r.status_code == 400
    assert "vendida" in r.json()["detail"].lower()