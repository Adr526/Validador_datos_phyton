import csv
from io import StringIO

from fastapi.responses import StreamingResponse
from datetime import date
import os
import shutil
import tempfile

from fastapi import File, UploadFile
from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import SessionLocal
from esquemas import EventoCrear, EventoRespuesta
from modelos import EventoDB
from operaciones_eventos import (
    ErrorBaseDatos,
    EventoDuplicadoError,
    guardar_evento,
    listar_eventos,
)
from validaciones import validar_eventos


app = FastAPI(
    title="Validador de Eventos API",
    description="API para validar, guardar y consultar eventos.",
    version="1.0.0",
)


def obtener_sesion() -> Generator[Session, None, None]:
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


@app.get("/")
def inicio():
    return {
        "mensaje": "API Validador de Eventos",
        "documentacion": "/docs",
    }


@app.post("/eventos/validar")
def validar_lista_eventos(solicitud: dict):
    eventos = solicitud.get("eventos", [])
    errores = validar_eventos(eventos)

    return {
        "total_eventos": len(eventos),
        "registros_con_errores": len(errores),
        "errores": errores,
    }


@app.post(
    "/eventos",
    response_model=EventoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_evento(
    evento: EventoCrear,
    sesion: Session = Depends(obtener_sesion),
):
    datos_validar = [
        {
            "id": evento.id_evento,
            "nombre": evento.nombre,
            "fecha": evento.fecha.isoformat(),
            "solicitante": evento.solicitante,
        }
    ]

    errores = validar_eventos(datos_validar)

    if errores:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=errores,
        )

    consulta = select(EventoDB).where(
        EventoDB.id_evento == evento.id_evento
    )

    try:
        evento_existente = sesion.scalar(consulta)

        if evento_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un evento con ese ID.",
            )

        return guardar_evento(
            sesion=sesion,
            id_evento=evento.id_evento,
            nombre=evento.nombre,
            fecha=evento.fecha,
            solicitante=evento.solicitante,
        )

    except EventoDuplicadoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un evento con ese ID.",
        ) from None

    except ErrorBaseDatos:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de almacenamiento no está disponible.",
        ) from None

    except SQLAlchemyError:
        sesion.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de almacenamiento no está disponible.",
        ) from None


@app.get(
    "/eventos",
    response_model=list[EventoRespuesta],
)
def consultar_eventos(
    sesion: Session = Depends(obtener_sesion),
):
    try:
        return listar_eventos(sesion)

    except ErrorBaseDatos:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de almacenamiento no está disponible.",
        ) from None


@app.post("/eventos/csv")
def cargar_eventos_csv(
    archivo: UploadFile = File(...),
    sesion: Session = Depends(obtener_sesion),
):
    ruta_temporal = None

    try:
        # Guardar temporalmente el archivo recibido.
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".csv",
            delete=False,
        ) as temporal:
            ruta_temporal = temporal.name
            shutil.copyfileobj(archivo.file, temporal)

        # Reutilizar el lector CSV existente.
        from archivos import cargar_eventos as leer_csv

        eventos = leer_csv(ruta_temporal)

        if not eventos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo CSV no contiene registros.",
            )

        # Validar todos los registros del archivo.
        errores_validacion = validar_eventos(eventos)

        # Relacionar los errores con sus registros.
        claves_con_error = {
            (error.get("id"), error.get("nombre"))
            for error in errores_validacion
        }

        # Identificar los eventos que superaron la validación.
        candidatos = [
            evento
            for evento in eventos
            if (evento.get("id"), evento.get("nombre"))
            not in claves_con_error
        ]

        # Consultar cuáles de esos identificadores ya existen.
        ids_candidatos = {
            evento["id"]
            for evento in candidatos
        }

        ids_existentes = set()

        if ids_candidatos:
            consulta = select(EventoDB.id_evento).where(
                EventoDB.id_evento.in_(ids_candidatos)
            )
            ids_existentes = set(sesion.scalars(consulta).all())

        # Informar los duplicados encontrados en PostgreSQL.
        errores = list(errores_validacion)

        for evento in candidatos:
            if evento["id"] in ids_existentes:
                errores.append({
                    "id": evento["id"],
                    "nombre": evento["nombre"],
                    "errores": [
                        "El ID ya existe en la base de datos."
                    ],
                })

        # Guardar cada evento válido de forma independiente.
        guardados = 0

        for evento in candidatos:
            if evento["id"] in ids_existentes:
                continue

            try:
                guardar_evento(
                    sesion=sesion,
                    id_evento=evento["id"],
                    nombre=evento["nombre"],
                    fecha=date.fromisoformat(evento["fecha"]),
                    solicitante=evento["solicitante"],
                )
                guardados += 1

            except EventoDuplicadoError:
                # Puede ocurrir si otra petición inserta el ID
                # después de nuestra consulta inicial.
                errores.append({
                    "id": evento["id"],
                    "nombre": evento["nombre"],
                    "errores": [
                        "El ID ya existe en la base de datos."
                    ],
                })

            except (ErrorBaseDatos, SQLAlchemyError):
                sesion.rollback()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No fue posible guardar los eventos.",
                ) from None


        resumen = {
            "total_eventos": len(eventos),
            "eventos_guardados": guardados,
            "registros_rechazados": len(eventos) - guardados,
        }

        # Si no hay errores, devolver el resumen como JSON.
        if not errores:
            return resumen

        # Si hay errores, generar un CSV descargable.
        salida = StringIO(newline="")
        escritor = csv.DictWriter(
            salida,
            fieldnames=["id", "nombre", "errores"],
        )
        escritor.writeheader()

        for resultado in errores:
            escritor.writerow({
                "id": resultado.get("id") or "",
                "nombre": resultado.get("nombre") or "",
                "errores": ", ".join(
                    str(motivo)
                    for motivo in resultado.get("errores", [])
                ),
            })

        contenido = "\ufeff" + salida.getvalue()

        return StreamingResponse(
            iter([contenido]),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": (
                    'attachment; filename="reporte_errores.csv"'
                ),
                "X-Total-Eventos": str(resumen["total_eventos"]),
                "X-Eventos-Guardados": str(resumen["eventos_guardados"]),
                "X-Registros-Rechazados": str(
                    resumen["registros_rechazados"]
                ),
            },
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from None

    except SQLAlchemyError:
        sesion.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar la base de datos.",
        ) from None

    finally:
        archivo.file.close()

        if ruta_temporal and os.path.exists(ruta_temporal):
            os.unlink(ruta_temporal)


@app.post("/eventos/errores/descargar")
def descargar_reporte_errores(solicitud: dict):
    errores = solicitud.get("errores", [])

    if not isinstance(errores, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El campo errores debe ser una lista.",
        )

    salida = StringIO()
    escritor = csv.DictWriter(
        salida,
        fieldnames=["id", "nombre", "errores"],
    )
    escritor.writeheader()

    for resultado in errores:
        if not isinstance(resultado, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Cada error debe ser un objeto.",
            )

        motivos = resultado.get("errores", [])

        if not isinstance(motivos, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Los motivos de error deben ser una lista.",
            )

        escritor.writerow({
            "id": resultado.get("id", ""),
            "nombre": resultado.get("nombre", ""),
            "errores": ", ".join(str(motivo) for motivo in motivos),
        })

    contenido = "\ufeff" + salida.getvalue()

    return StreamingResponse(
        iter([contenido]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_errores.csv"'
            )
        },
    )

