
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
    assert "text/csv" in respuesta.headers["content-type"]
    assert "reporte_errores.csv" in respuesta.headers["content-disposition"]
    assert respuesta.headers["X-Total-Eventos"] == "2"
    assert respuesta.headers["X-Eventos-Guardados"] == "1"
    assert respuesta.headers["X-Registros-Rechazados"] == "1"
    assert "EVT-CSV-102" in respuesta.text
    assert "Fecha invalida o ausente" in respuesta.text


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
    assert "text/csv" in segunda_respuesta.headers["content-type"]
    assert segunda_respuesta.headers["X-Eventos-Guardados"] == "0"
    assert segunda_respuesta.headers["X-Registros-Rechazados"] == "1"
    assert "EVT-CSV-103" in segunda_respuesta.text
    assert "ya existe" in segunda_respuesta.text


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


def test_csv_rechaza_todas_las_filas_con_id_duplicado(cliente_csv):
    contenido = (
        "id,nombre,fecha,solicitante\n"
        "EVT-CSV-105,Capacitacion,2026-10-15,Ana Perez\n"
        "EVT-CSV-105,Reunion,2026-10-16,Carlos Gomez\n"
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
    assert "text/csv" in respuesta.headers["content-type"]
    assert respuesta.headers["X-Total-Eventos"] == "2"
    assert respuesta.headers["X-Eventos-Guardados"] == "0"
    assert respuesta.headers["X-Registros-Rechazados"] == "2"
    assert respuesta.text.count("EVT-CSV-105") == 2
    assert respuesta.text.count("ID duplicado") == 2
