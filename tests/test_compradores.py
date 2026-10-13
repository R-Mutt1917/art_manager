from fastapi.testclient import TestClient

def test_registrar_venta_cambia_estado_de_obra(client: TestClient):
    """Test: Al registrar una venta, la obra cambia a 'vendida' y se asocia al comprador."""
    # 1. Crear técnica y obra disponible
    tecnica = client.post("/tecnicas/", json={"nombre": "Óleo", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Obra para Vender", "anio": 2024, "dimensiones": "50x50 cm",
        "precio": 2000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    # 2. Crear comprador
    comprador = client.post("/compradores/", json={
        "nombre": "Juan Pérez", "email": "juan@email.com"
    }).json()
    
    # 3. Registrar la venta
    response_venta = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador["id"],
        "fecha_venta": "2024-10-01"
    })
    
    assert response_venta.status_code == 201
    data_venta = response_venta.json()
    assert data_venta["mensaje"] == "Venta registrada exitosamente"
    assert data_venta["comprador_id"] == comprador["id"]
    
    # 4. Verificar que la obra ahora está vendida
    response_obra = client.get(f"/obras/{obra['id']}")
    assert response_obra.status_code == 200
    obra_actualizada = response_obra.json()
    assert obra_actualizada["estado"] == "vendida"
    assert obra_actualizada["comprador_id"] == comprador["id"]
    assert obra_actualizada["fecha_venta"] == "2024-10-01"

def test_no_se_puede_vender_una_obra_ya_vendida(client: TestClient):
    """Test: El sistema rechaza vender una obra que ya fue vendida previamente."""
    # 1. Crear técnica, obra (disponible) y dos compradores
    tecnica = client.post("/tecnicas/", json={"nombre": "Acuarela", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Obra a Vender Dos Veces", "anio": 2024, "dimensiones": "50x50 cm",
        "precio": 1000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    comprador1 = client.post("/compradores/", json={
        "nombre": "María López", "email": "maria@email.com"
    }).json()
    
    comprador2 = client.post("/compradores/", json={
        "nombre": "Carlos Ruiz", "email": "carlos@email.com"
    }).json()
    
    # 2. Primera venta (DEBE FUNCIONAR)
    response_venta1 = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador1["id"],
        "fecha_venta": "2024-10-01"
    })
    assert response_venta1.status_code == 201
    
    # 3. Intentar registrar una segunda venta para la MISMA obra (¡DEBE FALLAR!)
    response_venta2 = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador2["id"],
        "fecha_venta": "2024-10-05"
    })
    
    assert response_venta2.status_code == 400
    assert "ya está vendida" in response_venta2.json()["detail"]