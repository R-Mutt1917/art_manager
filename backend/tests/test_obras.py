from fastapi.testclient import TestClient

def test_crear_obra(client: TestClient):
    """Test: Crear una obra correctamente."""
    # 1. Crear una técnica
    tecnica_response = client.post(
        "/tecnicas/",
        json={"nombre": "Óleo", "descripcion": "Pintura con aceite"}
    )
    
    # Si falla, imprimimos el error real para saber por qué
    if tecnica_response.status_code != 201:
        print("ERROR AL CREAR TÉCNICA:", tecnica_response.json())
        
    assert tecnica_response.status_code == 201
    tecnica_id = tecnica_response.json()["id"]
    
    # 2. Crear la obra
    obra_data = {
        "titulo": "Atardecer en el Puerto",
        "anio": 2023,
        "dimensiones": "50x70 cm",
        "precio": 1500.00,
        "estado": "disponible",
        "notas": "Obra de prueba",
        "tecnica_id": tecnica_id
    }
    
    response = client.post("/obras/", json=obra_data)
    
    # 3. Verificamos
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Atardecer en el Puerto"
    assert data["precio"] == 1500.00

def test_listar_obras(client: TestClient):
    """Test: Listar todas las obras."""
    # 1. Crear técnica
    tecnica_response = client.post("/tecnicas/", json={"nombre": "Acuarela", "descripcion": "Agua"})
    tecnica_id = tecnica_response.json()["id"]
    
    # 2. Crear 2 obras
    for i in range(2):
        client.post("/obras/", json={
            "titulo": f"Obra {i}", "anio": 2023, "dimensiones": "50x70 cm",
            "precio": 1000.00, "estado": "disponible", "tecnica_id": tecnica_id
        })
    
    # 3. Listar y verificar
    response = client.get("/obras/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_soft_delete(client: TestClient):
    """Test: Soft delete de una obra."""
    # 1. Crear técnica y obra
    tecnica_response = client.post("/tecnicas/", json={"nombre": "Escultura", "descripcion": "Bronce"})
    tecnica_id = tecnica_response.json()["id"]
    
    obra_response = client.post("/obras/", json={
        "titulo": "Obra a Eliminar", "anio": 2023, "dimensiones": "30x30x50 cm",
        "precio": 3000.00, "estado": "disponible", "tecnica_id": tecnica_id
    })
    obra_id = obra_response.json()["id"]
    
    # 2. Eliminar (soft delete)
    delete_response = client.delete(f"/obras/{obra_id}")
    assert delete_response.status_code == 200
    assert "dada de baja" in delete_response.json()["mensaje"]
    
    # 3. Verificar que ya no aparece en la lista
    list_response = client.get("/obras/")
    assert len(list_response.json()) == 0
    
    # 4. Verificar que obtenerla por ID da 404
    get_response = client.get(f"/obras/{obra_id}")
    assert get_response.status_code == 404