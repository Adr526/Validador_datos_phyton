
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class EventoDB(Base):
    __tablename__ = "eventos"

    registro_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    id_evento: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    solicitante: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
