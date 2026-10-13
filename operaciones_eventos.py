
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from modelos import EventoDB


logger = logging.getLogger(__name__)


class ErrorBaseDatos(Exception):
    """Error controlado al acceder a la base de datos."""


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

    except SQLAlchemyError as error:
        sesion.rollback()

        logger.exception("Error al guardar un evento en la base de datos")

        raise ErrorBaseDatos(
            "No fue posible guardar el evento."
        ) from error


def listar_eventos(sesion: Session) -> list[EventoDB]:
    try:
        consulta = select(EventoDB).order_by(EventoDB.registro_id)
        return list(sesion.scalars(consulta).all())

    except SQLAlchemyError as error:
        logger.exception("Error al consultar eventos en la base de datos")

        raise ErrorBaseDatos(
            "No fue posible consultar los eventos."
        ) from error

