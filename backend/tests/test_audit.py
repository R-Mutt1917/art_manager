"""Tests de auditoría (Fase 2.9)."""
from fastapi.testclient import TestClient


def _login_admin(client: TestClient) -> dict:
    r = client.post("/auth/login", json={
        "email": "admin@artmanager.com",
        "password": "admin123",
    })
    assert r.status_code == 200, r.json()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_login_exitoso_genera_audit_log(client: TestClient):
    """Un login exitoso debe quedar registrado en audit_logs."""
    client.post("/auth/register", json={
        "email": "audit_user@example.com",
        "nombre": "Audit User",
        "password": "password123",
    })
    client.post("/auth/login", json={
        "email": "audit_user@example.com",
        "password": "password123",
    })

    r = client.get("/audit/logs?limit=50", headers=_login_admin(client))
    assert r.status_code == 200, r.json()

    logs = [
        log for log in r.json()
        if log["tipo_evento"] == "login_exitoso"
        and log["usuario_email"] == "audit_user@example.com"
    ]
    assert len(logs) >= 1


def test_login_fallido_genera_audit_log(client: TestClient):
    """Un login fallido debe quedar registrado (detección de fuerza bruta)."""
    client.post("/auth/login", json={
        "email": "fantasma@example.com",
        "password": "incorrecta",
    })

    r = client.get(
        "/audit/logs?tipo_evento=login_fallido&limit=50",
        headers=_login_admin(client),
    )
    assert r.status_code == 200, r.json()
    assert len(r.json()) >= 1


def test_logs_requiere_rol_admin(client: TestClient):
    """Un usuario VIEWER no puede ver los logs de auditoría."""
    client.post("/auth/register", json={
        "email": "viewer_audit@example.com",
        "nombre": "Viewer Audit",
        "password": "viewer123",
    })
    r_login = client.post("/auth/login", json={
        "email": "viewer_audit@example.com",
        "password": "viewer123",
    })
    viewer_headers = {"Authorization": f"Bearer {r_login.json()['access_token']}"}

    r = client.get("/audit/logs", headers=viewer_headers)
    assert r.status_code == 403