import os

from dotenv import load_dotenv
from sqlalchemy import URL


load_dotenv()


class Configuracion:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "validador_eventos")

    @property
    def database_url(self) -> URL:
        if not self.DB_PASSWORD:
            raise RuntimeError(
                "Falta configurar la variable de entorno DB_PASSWORD."
            )

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


configuracion = Configuracion()
