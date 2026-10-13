import csv
import pytest
from archivos import cargar_eventos, exportar_errores


def test_cargar_eventos(tmp_path):
    archivo = tmp_path / "eventos.csv"

    archivo.write_text(
        "id,nombre,fecha,solicitante\n"
        "101,Capacitacion,2026-11-15,Laura\n"
        "102,Congreso,2026-12-01,Carlos\n",
        encoding="utf-8"
    )

    eventos = cargar_eventos(str(archivo))

    assert len(eventos) == 2
    assert eventos[0]["id"] == "101"
    assert eventos[0]["nombre"] == "Capacitacion"
    assert eventos[1]["solicitante"] == "Carlos"


def test_cargar_eventos_sin_columna_obligatoria(tmp_path):
    archivo = tmp_path / "eventos.csv"

    archivo.write_text(
        "id,nombre,solicitante\n"
        "101,Capacitacion,Laura\n",
        encoding="utf-8"
    )

    try:
        cargar_eventos(str(archivo))
    except ValueError as error:
        assert "Faltan columnas" in str(error)
    else:
        raise AssertionError("Se esperaba un ValueError por columnas faltantes")


def test_exportar_errores(tmp_path):
    archivo = tmp_path / "reporte_errores.csv"

    resultados = [
        {
            "id": "102",
            "nombre": "Congreso",
            "errores": ["Fecha invalida o ausente"]
        }
    ]

    exportar_errores(resultados, str(archivo))

    with archivo.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as entrada:
        filas = list(csv.DictReader(entrada))

    assert len(filas) == 1
    assert filas[0]["id"] == "102"
    assert filas[0]["nombre"] == "Congreso"
    assert filas[0]["errores"] == "Fecha invalida o ausente"
