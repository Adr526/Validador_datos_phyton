from sqlalchemy import text

from database import engine

with engine.connect() as conexion:
    resultado = conexion.execute(text("SELECT current_database()"))
    nombre_bd = resultado.scalar_one()

    print(f"Conexión exitosa. Base de datos: {nombre_bd}")