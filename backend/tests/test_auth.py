"""Tests del módulo de Autenticación (Fase 2A)."""
from fastapi.testclient import TestClient

CREDENCIALES = {
    "email": "nuevo@example.com",
    "nombre": "Usuario Nuevo",
    "password": "password123",
}


def _registrar(client: TestClient, datos: dict | None = None):
    return client.post("/auth/register", json=datos or CREDENCIALES)


def _login(client: TestClient, email: str, password: str):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register_crea_usuario_con_rol_viewer(client: TestClient):
    r = _registrar(client)
    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["email"] == CREDENCIALES["email"]
    assert data["rol"] == "viewer"          # seguridad por defecto
    assert "password" not in data           # nunca exponer la contraseña
    assert "password_hash" not in data


def test_register_email_duplicado_devuelve_409(client: TestClient):
    assert _registrar(client).status_code == 201
    r2 = _registrar(client)
    assert r2.status_code == 409


def test_register_password_corta_devuelve_422(client: TestClient):
    r = _registrar(client, {**CREDENCIALES, "password": "corta"})
    assert r.status_code == 422


def test_login_ok_devuelve_par_de_tokens(client: TestClient):
    _registrar(client)
    r = _login(client, CREDENCIALES["email"], CREDENCIALES["password"])
    assert r.status_code == 200, r.json()
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_con_credenciales_invalidas_devuelve_401(client: TestClient):
    r = _login(client, "fantasma@example.com", "malpassword")
    assert r.status_code == 401


def test_refresh_canjea_tokens_correctamente(client: TestClient):
    _registrar(client)
    tokens = _login(client, CREDENCIALES["email"], CREDENCIALES["password"]).json()

    r = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200, r.json()
    assert r.json()["access_token"]


def test_refresh_rechaza_un_access_token(client: TestClient):
    """Un access token NO debe servir como refresh (separa responsabilidades)."""
    _registrar(client)
    tokens = _login(client, CREDENCIALES["email"], CREDENCIALES["password"]).json()

    r = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401


def test_seed_crea_usuario_admin(client: TestClient):
    """El admin sembrado debe poder loguearse."""
    r = _login(client, "admin@artmanager.com", "admin123")
    assert r.status_code == 200, r.json()