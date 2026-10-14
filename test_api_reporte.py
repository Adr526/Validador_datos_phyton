
from fastapi.testclient import TestClient

from api import app

cliente = TestClient(app)


def test_descargar_reporte_csv():
    solicitud = {
        "errores": [
            {
                "id": "EVT-301",
                "nombre": "Capacitacion",
                "errores": ["Fecha invalida o ausente"],
            }
        ]
    }

    respuesta = cliente.post(
        "/eventos/errores/descargar",
        json=solicitud,
    )

    assert respuesta.status_code == 200
    assert "text/csv" in respuesta.headers["content-type"]
    assert "attachment;" in respuesta.headers["content-disposition"]
    assert "EVT-301" in respuesta.text
    assert "Fecha invalida o ausente" in respuesta.text


def test_descargar_reporte_sin_errores():
    respuesta = cliente.post(
        "/eventos/errores/descargar",
        json={"errores": []},
    )

    assert respuesta.status_code == 200
    assert "id,nombre,errores" in respuesta.text


def test_rechazar_errores_con_formato_incorrecto():
    respuesta = cliente.post(
        "/eventos/errores/descargar",
        json={"errores": "no es una lista"},
    )

    assert respuesta.status_code == 422
