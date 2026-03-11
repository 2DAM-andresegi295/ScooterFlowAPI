import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app

ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_scooterflow.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    previous_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url

    alembic_cfg = Config(str(ROOT_DIR / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()
        engine.dispose()
        if previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_database_url


def crear_zona(client):
    response = client.post(
        "/zonas/",
        json={
            "nombre": "Centro Histórico",
            "codigo_postal": "28012",
            "limite_velocidad": 25,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_crear_zona(client):
    zona = crear_zona(client)
    assert zona["nombre"] == "Centro Histórico"


def test_crear_scooter(client):
    zona = crear_zona(client)
    response = client.post(
        "/scooters/",
        json={
            "numero_serie": "ABC123",
            "modelo": "Xiaomi",
            "bateria": 80,
            "estado": "disponible",
            "zona_id": zona["id"],
        },
    )
    assert response.status_code == 201
    assert response.json()["numero_serie"] == "ABC123"


def test_bateria_invalida(client):
    zona = crear_zona(client)
    response = client.post(
        "/scooters/",
        json={
            "numero_serie": "BATERR",
            "modelo": "Xiaomi",
            "bateria": 150,
            "estado": "disponible",
            "zona_id": zona["id"],
        },
    )
    assert response.status_code == 422


def test_mantenimiento_zona(client):
    zona = crear_zona(client)
    create_response = client.post(
        "/scooters/",
        json={
            "numero_serie": "LOWBAT1",
            "modelo": "Xiaomi",
            "bateria": 10,
            "estado": "disponible",
            "zona_id": zona["id"],
        },
    )
    assert create_response.status_code == 201

    response = client.post(f"/zonas/{zona['id']}/mantenimiento")
    assert response.status_code == 200
    assert response.json()["actualizados"] == 1


def test_scooter_vinculado_zona(client):
    zona = crear_zona(client)
    response = client.post(
        "/scooters/",
        json={
            "numero_serie": "ZONECHK1",
            "modelo": "Xiaomi",
            "bateria": 80,
            "estado": "disponible",
            "zona_id": zona["id"],
        },
    )
    assert response.status_code == 201
    assert response.json()["zona_id"] == zona["id"]


def test_docs_usa_assets_locales(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "/swagger-static/swagger-ui-bundle.js" in response.text
    assert "/swagger-static/swagger-ui.css" in response.text


def test_swagger_assets_locales_disponibles(client):
    js_response = client.get("/swagger-static/swagger-ui-bundle.js")
    css_response = client.get("/swagger-static/swagger-ui.css")
    assert js_response.status_code == 200
    assert css_response.status_code == 200


def test_openapi_version_compatible_con_swagger_local(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["openapi"] == "3.0.3"
