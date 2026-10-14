
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app, obtener_sesion
from database import Base
from modelos import EventoDB


@pytest.fixture
def cliente_csv():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=motor)

    SesionPrueba = sessionmaker(
        bind=motor,
        autoflush=False,
        autocommit=False,
    )

    def obtener_sesion_prueba():
        sesion = SesionPrueba()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[obtener_sesion] = obtener_sesion_prueba

    with TestClient(app) as cliente:
        yield cliente

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=motor)
    motor.dispose()


def test_csv_guarda_validos_y_rechaza_fecha_invalida(cliente_csv):
    contenido = (
        "id,nombre,fecha,solicitante\n"
        "EVT-CSV-101,Capacitacion,2026-10-15,Ana Perez\n"
        "EVT-CSV-102,Reunion,fecha_invalida,Carlos Gomez\n"
    )

    respuesta = cliente_csv.post(
        "/eventos/csv",
        files={
            "archivo": (
                "eventos.csv",
                BytesIO(contenido.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert resultado["total_eventos"] == 2
    assert resultado["eventos_guardados"] == 1
    assert resultado["registros_rechazados"] == 1
    assert len(resultado["errores"]) == 1
    assert resultado["errores"][0]["id"] == "EVT-CSV-102"


def test_csv_rechaza_id_que_ya_existe(cliente_csv):
    contenido = (
        "id,nombre,fecha,solicitante\n"
        "EVT-CSV-103,Capacitacion,2026-10-15,Ana Perez\n"
    )

    primera_respuesta = cliente_csv.post(
        "/eventos/csv",
        files={
            "archivo": (
                "eventos.csv",
                BytesIO(contenido.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert primera_respuesta.status_code == 200
    assert primera_respuesta.json()["eventos_guardados"] == 1

    segunda_respuesta = cliente_csv.post(
        "/eventos/csv",
        files={
            "archivo": (
                "eventos.csv",
                BytesIO(contenido.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert segunda_respuesta.status_code == 200

    resultado = segunda_respuesta.json()
    assert resultado["eventos_guardados"] == 0
    assert resultado["registros_rechazados"] == 1
    assert "ya existe" in resultado["errores"][0]["errores"][0]


def test_csv_rechaza_archivo_sin_columnas_requeridas(cliente_csv):
    contenido = (
        "codigo,descripcion\n"
        "EVT-CSV-104,Capacitacion\n"
    )

    respuesta = cliente_csv.post(
        "/eventos/csv",
        files={
            "archivo": (
                "eventos.csv",
                BytesIO(contenido.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert respuesta.status_code == 400
    assert "Faltan columnas requeridas" in respuesta.json()["detail"]
