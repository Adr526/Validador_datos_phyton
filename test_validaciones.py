
from validaciones import (
    validar_solicitante,
    validar_fecha,
    detectar_duplicados,
    validar_eventos
)


def test_solicitante_valido():
    assert validar_solicitante("Laura") is True


def test_solicitante_vacio():
    assert validar_solicitante("") is False


def test_solicitante_con_espacios():
    assert validar_solicitante("   ") is False


def test_solicitante_none():
    assert validar_solicitante(None) is False


def test_fecha_valida():
    assert validar_fecha("2026-11-15") is True


def test_fecha_invalida():
    assert validar_fecha("2026-13-40") is False


def test_fecha_none():
    assert validar_fecha(None) is False


def test_detectar_duplicados():
    eventos = [
        {"id": 101},
        {"id": 102},
        {"id": 101}
    ]

    assert detectar_duplicados(eventos) == {101}


def test_validar_eventos():
    eventos = [
        {
            "id": 101,
            "nombre": "Capacitacion",
            "fecha": "2026-11-15",
            "solicitante": "Laura"
        },
        {
            "id": 102,
            "nombre": "Congreso",
            "fecha": "2026-13-40",
            "solicitante": ""
        }
    ]

    resultados = validar_eventos(eventos)

    assert len(resultados) == 1
    assert resultados[0]["id"] == 102
    assert "Fecha invalida o ausente" in resultados[0]["errores"]
    assert "Solicitante vacio o invalido" in resultados[0]["errores"]
