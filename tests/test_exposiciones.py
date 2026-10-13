from fastapi.testclient import TestClient

def test_asignar_obra_a_exposicion_sin_superposicion(client: TestClient):
    """Test: Asignar una obra a una exposición funciona correctamente."""
    # 1. Crear técnica y obra
    tecnica = client.post("/tecnicas/", json={"nombre": "Óleo", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Obra de Prueba", "anio": 2024, "dimensiones": "50x50 cm",
        "precio": 1000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    # 2. Crear exposición
    expo = client.post("/exposiciones/", json={
        "nombre": "Expo Primavera", "lugar": "Galería Central",
        "fecha_inicio": "2024-03-01", "fecha_fin": "2024-03-15"
    }).json()
    
    # 3. Asignar obra a la exposición
    response = client.post(f"/exposiciones/{expo['id']}/obras/{obra['id']}", json={
        "sala": "Sala A", "pared": "Norte"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["obra_id"] == obra["id"]
    assert data["exposicion_id"] == expo["id"]

def test_rechazar_asignacion_con_fechas_superpuestas(client: TestClient):
    """
    Test CRÍTICO: El sistema RECHAZA asignar una obra si ya está en otra 
    exposición con fechas que se solapan.
    """
    # 1. Crear técnica y obra
    tecnica = client.post("/tecnicas/", json={"nombre": "Acuarela", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Obra Conflictiva", "anio": 2024, "dimensiones": "50x50 cm",
        "precio": 1000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    # 2. Crear PRIMERA exposición (1 al 15 de Marzo)
    expo1 = client.post("/exposiciones/", json={
        "nombre": "Expo 1", "lugar": "Lugar 1",
        "fecha_inicio": "2024-03-01", "fecha_fin": "2024-03-15"
    }).json()
    
    # Asignar obra a expo1 (debe funcionar)
    client.post(f"/exposiciones/{expo1['id']}/obras/{obra['id']}", json={"sala": "A"}).json()
    
    # 3. Crear SEGUNDA exposición con fechas superpuestas (10 al 25 de Marzo)
    expo2 = client.post("/exposiciones/", json={
        "nombre": "Expo 2", "lugar": "Lugar 2",
        "fecha_inicio": "2024-03-10", "fecha_fin": "2024-03-25"
    }).json()
    
    # 4. Intentar asignar la MISMA obra a la expo2 (¡DEBE FALLAR!)
    response = client.post(f"/exposiciones/{expo2['id']}/obras/{obra['id']}", json={"sala": "B"})
    
    assert response.status_code == 400
    assert "ya está asignada a otra exposición en fechas que se superponen" in response.json()["detail"]

def test_checklist_de_retiro(client: TestClient):
    """Test: Generar checklist de obras para retirar al finalizar una exposición."""
    # 1. Crear técnica, obra y exposición
    tecnica = client.post("/tecnicas/", json={"nombre": "Escultura", "descripcion": "Test"}).json()
    obra = client.post("/obras/", json={
        "titulo": "Escultura a Retirar", "anio": 2024, "dimensiones": "30x30x30 cm",
        "precio": 5000.0, "estado": "disponible", "tecnica_id": tecnica["id"]
    }).json()
    
    expo = client.post("/exposiciones/", json={
        "nombre": "Expo Final", "lugar": "Museo",
        "fecha_inicio": "2024-05-01", "fecha_fin": "2024-05-10"
    }).json()
    
    # 2. Asignar obra
    client.post(f"/exposiciones/{expo['id']}/obras/{obra['id']}", json={
        "sala": "Sala Principal", "pared": "Centro"
    })
    
    # 3. Solicitar checklist
    response = client.get(f"/exposiciones/{expo['id']}/checklist")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["titulo_obra"] == "Escultura a Retirar"
    assert data[0]["sala"] == "Sala Principal"