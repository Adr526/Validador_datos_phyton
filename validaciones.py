
from datetime import datetime


def validar_solicitante(solicitante):
    return isinstance(solicitante, str) and solicitante.strip() != ""


def validar_fecha(fecha):
    if not isinstance(fecha, str):
        return False

    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def detectar_duplicados(eventos):
    identificadores_vistos = set()
    duplicados = set()

    for evento in eventos:
        identificador = evento.get("id")

        if identificador is None or identificador == "":
            continue

        if identificador in identificadores_vistos:
            duplicados.add(identificador)
        else:
            identificadores_vistos.add(identificador)

    return duplicados


def validar_eventos(eventos):
    errores = []
    duplicados = detectar_duplicados(eventos)

    for posicion, evento in enumerate(eventos, start=1):
        errores_evento = []

        if not isinstance(evento, dict):
            errores.append({
                "id": None,
                "nombre": "Registro " + str(posicion),
                "errores": ["El registro no es un diccionario"]
            })
            continue

        identificador = evento.get("id")
        nombre = evento.get("nombre", "Sin nombre")
        solicitante = evento.get("solicitante")
        fecha = evento.get("fecha")

        if identificador is None or identificador == "":
            errores_evento.append("ID vacio")

        if not validar_solicitante(solicitante):
            errores_evento.append("Solicitante vacio o invalido")

        if not validar_fecha(fecha):
            errores_evento.append("Fecha invalida o ausente")

        if identificador in duplicados:
            errores_evento.append("ID duplicado")

        if errores_evento:
            errores.append({
                "id": identificador,
                "nombre": nombre,
                "errores": errores_evento
            })

    return errores
