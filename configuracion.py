
import os

from dotenv import load_dotenv

load_dotenv()


class Configuracion:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "validador_eventos")

    @property
    def database_url(self):
        if not self.DB_PASSWORD:
            raise RuntimeError(
                "Falta configurar la variable de entorno DB_PASSWORD."
            )

        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


configuracion = Configuracion()
