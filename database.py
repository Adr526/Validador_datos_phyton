
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from configuracion import configuracion


engine = create_engine(configuracion.database_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass
