
from database import Base, engine
from modelos import EventoDB


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")


if __name__ == "__main__":
    crear_tablas()
