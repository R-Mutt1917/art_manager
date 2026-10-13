from fastapi.testclient import TestClient

def test_ciclo_completo_de_prestamo(client: TestClient):
    """Test: Prestar una obra cambia su estado a 'en_prestamo', y al devolverla vuelve a 'disponible'."""
    # 1. Crear técnica y obra disponible
    tecnica = client.post("/tecnicas/", json={"nombre": "Escultura", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Escultura en Préstamo", "anio": 2024, "dimensiones": "30x30x30 cm",
        "precio": 5000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    # 2. Registrar el préstamo
    response_prestamo = client.post("/prestamos/", json={
        "obra_id": obra["id"],
        "prestatario_nombre": "Museo de Arte",
        "fecha_prestamo": "2024-11-01",
        "fecha_devolucion_esperada": "2024-12-01",
        "motivo": "Exposición temporal"
    })
    
    assert response_prestamo.status_code == 201
    prestamo_id = response_prestamo.json()["id"]
    
    # 3. Verificar que la obra cambió de estado
    response_obra = client.get(f"/obras/{obra['id']}")
    assert response_obra.json()["estado"] == "en_prestamo"
    
    # 4. Registrar la devolución
    response_devolucion = client.post(f"/prestamos/{prestamo_id}/devolucion", json={
        "fecha_devolucion_real": "2024-11-25",
        "estado_obra_tras_devolucion": "disponible"
    })
    
    assert response_devolucion.status_code == 200
    assert response_devolucion.json()["nuevo_estado_obra"] == "disponible"
    
    # 5. Verificar que la obra volvió a estar disponible
    response_obra_final = client.get(f"/obras/{obra['id']}")
    assert response_obra_final.json()["estado"] == "disponible"

def test_no_se_puede_prestar_una_obra_vendida(client: TestClient):
    """Test: El sistema rechaza prestar una obra que ya fue vendida."""
    # 1. Crear técnica, obra (disponible) y un comprador
    tecnica = client.post("/tecnicas/", json={"nombre": "Fotografía", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Foto a Vender y Prestar", "anio": 2024, "dimensiones": "40x50 cm",
        "precio": 800.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    comprador = client.post("/compradores/", json={
        "nombre": "Comprador Test", "email": "comprador@test.com"
    }).json()
    
    # 2. Vender la obra primero (esto cambia su estado a 'vendida')
    client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador["id"],
        "fecha_venta": "2024-10-01"
    })
    
    # 3. Intentar prestar la obra vendida (¡DEBE FALLAR!)
    response = client.post("/prestamos/", json={
        "obra_id": obra["id"],
        "prestatario_nombre": "Galería X",
        "fecha_prestamo": "2024-11-01",
        "fecha_devolucion_esperada": "2024-12-01"
    })
    
    assert response.status_code == 400
    assert "ya está vendida" in response.json()["detail"]