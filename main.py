from datetime import datetime
from archivos import cargar_eventos, exportar_errores
import csv
from validaciones import validar_eventos
import argparse

eventos = [
    {
        "id": 101,
        "nombre": "Capacitacion",
        "fecha": "2026-11-15",
        "solicitante": "Laura"
    },
    {
        "id": 102,
        "nombre": "Lanzamiento",
        "fecha": "2026-13-40",
        "solicitante": "Carlos"
    },
    {
        "id": 103,
        "nombre": "Congreso",
        "fecha": "2026-12-01",
        "solicitante": ""
    },
    {
        "id": 101,
        "nombre": "Capacitacion",
        "fecha": "2026-11-15",
        "solicitante": "Laura"
    }
]

# BLOQUE DE FUNCIONES
def cargar_eventos(ruta_archivo):
    eventos = []
    columnas_requeridas = {
        "id",
        "nombre",
        "fecha",
        "solicitante"
    }

    with open(
        ruta_archivo,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:

        lector = csv.DictReader(archivo)

        if lector.fieldnames is None:
            raise ValueError("El archivo CSV no tiene encabezados.")

        # Limpiar espacios de los encabezados
        lector.fieldnames = [
            columna.strip().lower()
            for columna in lector.fieldnames
        ]

        columnas_encontradas = set(lector.fieldnames)
        columnas_faltantes = columnas_requeridas - columnas_encontradas

        if columnas_faltantes:
            raise ValueError(
                f"Faltan columnas requeridas: {sorted(columnas_faltantes)}"
            )

        for numero_fila, fila in enumerate(lector, start=2):
            if None in fila:
                raise ValueError(
                    f"La fila {numero_fila} tiene más valores que columnas."
                )

            evento = {
                "id": fila["id"],
                "nombre": fila["nombre"],
                "fecha": fila["fecha"],
                "solicitante": fila["solicitante"]
            }

            eventos.append(evento)

    return eventos


def exportar_errores(resultados, ruta_salida):
    columnas = ["id", "nombre", "errores"]

    with open(
        ruta_salida,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )

        escritor.writeheader()

        for resultado in resultados:
            escritor.writerow({
                "id": resultado["id"],
                "nombre": resultado["nombre"],
                "errores": ", ".join(resultado["errores"])
            })

    print(f"Reporte generado: {ruta_salida}")


# BLOQUE PRINCIPAL



def main():
    parser = argparse.ArgumentParser(
        description="Valida eventos desde un archivo CSV."
    )

    parser.add_argument(
        "archivo_entrada",
        help="Ruta del archivo CSV que contiene los eventos."
    )

    parser.add_argument(
        "archivo_salida",
        help="Ruta donde se guardara el reporte de errores."
    )

    args = parser.parse_args()

    print("Validador de eventos")

    try:
        eventos = cargar_eventos(args.archivo_entrada)

        print(f"Eventos cargados: {len(eventos)}")

        resultados = validar_eventos(eventos)

        exportar_errores(
            resultados,
            args.archivo_salida
        )

        if resultados:
            print(
                f"Se encontraron {len(resultados)} "
                "registros con errores."
            )
        else:
            print("No se encontraron errores.")

    except (FileNotFoundError, ValueError, csv.Error) as error:
        print(f"Error al procesar el archivo: {error}")


if __name__ == "__main__":
    main()

