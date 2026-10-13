from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_inicio_api():
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "API Validador de Eventos"


def test_validar_evento_correcto():
    datos = {
        "eventos": [
            {
                "id": "101",
                "nombre": "Capacitacion",
                "fecha": "2026-11-15",
                "solicitante": "Laura"
            }
        ]
    }

    respuesta = client.post("/eventos/validar", json=datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["total_eventos"] == 1
    assert respuesta.json()["registros_con_errores"] == 0


def test_validar_fecha_incorrecta():
    datos = {
        "eventos": [
            {
                "id": "102",
                "nombre": "Lanzamiento",
                "fecha": "2026-13-40",
                "solicitante": "Carlos"
            }
        ]
    }

    respuesta = client.post("/eventos/validar", json=datos)

    assert respuesta.status_code == 200
    resultado = respuesta.json()

    assert resultado["registros_con_errores"] == 1
    assert "Fecha invalida o ausente" in resultado["errores"][0]["errores"]


def test_detectar_ids_duplicados():
    datos = {
        "eventos": [
            {
                "id": "101",
                "nombre": "Capacitacion",
                "fecha": "2026-11-15",
                "solicitante": "Laura"
            },
            {
                "id": "101",
                "nombre": "Congreso",
                "fecha": "2026-12-15",
                "solicitante": "Carlos"
            }
        ]
    }

    respuesta = client.post("/eventos/validar", json=datos)

    assert respuesta.status_code == 200
    resultado = respuesta.json()

    assert resultado["registros_con_errores"] == 2

    for registro in resultado["errores"]:
        assert "ID duplicado" in registro["errores"]
