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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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