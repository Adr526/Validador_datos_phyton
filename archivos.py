import csv

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