from fastapi.testclient import TestClient

def test_crear_y_obtener_tecnica_por_id(client: TestClient):
    """
    Test CRÍTICO: Crear una técnica y recuperarla individualmente por su ID.
    Este test confirmará si el endpoint GET /tecnicas/{id} está funcionando.
    """
    # 1. Crear una técnica
    response_crear = client.post(
        "/tecnicas/",
        json={"nombre": "Óleo sobre lienzo", "descripcion": "Técnica clásica de prueba"}
    )
    assert response_crear.status_code == 201
    data_creada = response_crear.json()
    tecnica_id = data_creada["id"]
    
    # 2. Obtener la técnica por su ID (Aquí es donde sospechamos que falla)
    response_obtener = client.get(f"/tecnicas/{tecnica_id}")
    
    # Si el router está bien, esto será 200. Si está roto, será 404 o 500.
    assert response_obtener.status_code == 200, f"Esperaba 200, pero obtuvo {response_obtener.status_code}. Detalle: {response_obtener.json()}"
    assert response_obtener.json()["nombre"] == "Óleo sobre lienzo"

def test_listar_tecnicas(client: TestClient):
    """Test: Listar todas las técnicas."""
    # Crear una para asegurar que hay datos
    client.post("/tecnicas/", json={"nombre": "Acuarela", "descripcion": "Agua"})
    
    response = client.get("/tecnicas/")
    assert response.status_code == 200
    assert len(response.json()) >= 1