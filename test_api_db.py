
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app, obtener_sesion
from database import Base
from modelos import EventoDB


# Base de datos temporal exclusiva para las pruebas.
# No utiliza tu PostgreSQL real.
engine_pruebas = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SesionPruebas = sessionmaker(
    bind=engine_pruebas,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def cliente():
    Base.metadata.create_all(bind=engine_pruebas)

    def obtener_sesion_pruebas():
        sesion = SesionPruebas()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[obtener_sesion] = (
        obtener_sesion_pruebas
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_pruebas)


def test_crear_evento(cliente):
    datos = {
        "id_evento": "EVT-TEST-001",
        "nombre": "Capacitacion",
        "fecha": "2026-11-15",
        "solicitante": "Laura"
    }

    respuesta = cliente.post("/eventos", json=datos)

    assert respuesta.status_code == 201
    resultado = respuesta.json()

    assert resultado["id_evento"] == "EVT-TEST-001"
    assert resultado["nombre"] == "Capacitacion"
    assert resultado["solicitante"] == "Laura"
    assert resultado["registro_id"] is not None


def test_consultar_eventos(cliente):
    datos = {
        "id_evento": "EVT-TEST-002",
        "nombre": "Congreso",
        "fecha": "2026-12-01",
        "solicitante": "Carlos"
    }

    cliente.post("/eventos", json=datos)

    respuesta = cliente.get("/eventos")

    assert respuesta.status_code == 200
    resultados = respuesta.json()

    assert len(resultados) == 1
    assert resultados[0]["id_evento"] == "EVT-TEST-002"


def test_rechazar_fecha_invalida(cliente):
    datos = {
        "id_evento": "EVT-TEST-003",
        "nombre": "Lanzamiento",
        "fecha": "2026-13-40",
        "solicitante": "Carlos"
    }

    respuesta = cliente.post("/eventos", json=datos)

    assert respuesta.status_code == 422


def test_rechazar_solicitante_vacio(cliente):
    datos = {
        "id_evento": "EVT-TEST-101",
        "nombre": "Congreso",
        "fecha": "2026-12-01",
        "solicitante": ""
    }

    respuesta = cliente.post("/eventos", json=datos)

    assert respuesta.status_code == 422
    assert "Solicitante vacio o invalido" in str(
        respuesta.json()
    )


def test_rechazar_id_duplicado(cliente):
    datos = {
        "id_evento": "EVT-TEST-102",
        "nombre": "Capacitacion",
        "fecha": "2026-11-15",
        "solicitante": "Laura"
    }

    primera_respuesta = cliente.post("/eventos", json=datos)

    assert primera_respuesta.status_code == 201

    segunda_respuesta = cliente.post("/eventos", json=datos)

    assert segunda_respuesta.status_code == 409
    assert segunda_respuesta.json()["detail"] == (
        "Ya existe un evento con ese ID."
    )

