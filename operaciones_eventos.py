import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from modelos import EventoDB


logger = logging.getLogger(__name__)


class ErrorBaseDatos(Exception):
    """Error controlado al acceder a la base de datos."""


class EventoDuplicadoError(Exception):
    """Se intentó guardar un evento con un identificador existente."""


def guardar_evento(
    sesion: Session,
    id_evento: str,
    nombre: str,
    fecha,
    solicitante: str
) -> EventoDB:
    evento = EventoDB(
        id_evento=id_evento,
        nombre=nombre,
        fecha=fecha,
        solicitante=solicitante
    )

    try:
        sesion.add(evento)
        sesion.commit()
        sesion.refresh(evento)
        return evento

    except IntegrityError as error:
        sesion.rollback()

        if (
            getattr(error.orig, "sqlstate", None) == "23505"
            or getattr(error.orig, "pgcode", None) == "23505"
        ):
            logger.warning(
                "Se rechazó un evento con identificador duplicado."
            )
            raise EventoDuplicadoError(
                "Ya existe un evento con ese ID."
            ) from error

        logger.exception(
            "Error de integridad al guardar un evento."
        )
        raise ErrorBaseDatos(
            "No fue posible guardar el evento."
        ) from error

    except SQLAlchemyError as error:
        sesion.rollback()
        logger.exception(
            "Error al guardar un evento en la base de datos."
        )
        raise ErrorBaseDatos(
            "No fue posible guardar el evento."
        ) from error


def listar_eventos(sesion: Session) -> list[EventoDB]:
    try:
        consulta = select(EventoDB).order_by(
            EventoDB.registro_id
        )
        return list(sesion.scalars(consulta).all())

    except SQLAlchemyError as error:
        logger.exception(
            "Error al consultar eventos en la base de datos."
        )
        raise ErrorBaseDatos(
            "No fue posible consultar los eventos."
        ) from error

