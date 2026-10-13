
from datetime import date

from pydantic import BaseModel, ConfigDict


class EventoCrear(BaseModel):
    id_evento: str
    nombre: str
    fecha: date
    solicitante: str


class EventoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    registro_id: int
    id_evento: str
    nombre: str
    fecha: date
    solicitante: str
