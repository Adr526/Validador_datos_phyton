
# Validador de Eventos

Aplicación desarrollada en Python para validar registros de eventos
empresariales desde archivos CSV.

## Funcionalidades

- Lectura de archivos CSV.
- Validación de campos obligatorios.
- Validación de fechas.
- Detección de identificadores duplicados.
- Exportación de errores a otro archivo CSV.
- Pruebas automatizadas con pytest.

## Tecnologías

- Python
- pytest
- Módulo csv de Python

## Requisitos

- Python 3.11 o superior
- pytest

## Instalación

Instalar las dependencias:

    python -m pip install pytest

## Ejecución

    python main.py eventos.csv reporte_errores.csv

## Pruebas

    python -m pytest -v

## Estructura

- main.py: coordina la ejecución.
- archivos.py: lee y exporta archivos CSV.
- validaciones.py: contiene las reglas de validación.
- test_archivos.py: prueba las funciones de archivos.
- test_validaciones.py: prueba las validaciones.
