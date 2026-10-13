# Validador de Eventos API

API REST desarrollada en Python para validar, registrar y consultar eventos. El proyecto permite detectar registros inválidos, validar fechas y campos obligatorios, identificar IDs duplicados y almacenar eventos en PostgreSQL.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- PostgreSQL 18
- SQLAlchemy
- Pydantic
- Pytest
- SQLite en memoria para pruebas automatizadas

## Funcionalidades

- Validación de campos obligatorios.
- Validación del formato de las fechas.
- Detección de IDs duplicados.
- Carga y exportación de datos CSV.
- Registro de eventos en PostgreSQL.
- Consulta de eventos almacenados.
- Respuestas HTTP para operaciones exitosas y errores de validación.
- Pruebas automatizadas de la lógica de negocio y de la API.

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Comprueba que la API está disponible. |
| POST | `/eventos/validar` | Valida una lista de eventos. |
| POST | `/eventos` | Registra un evento en PostgreSQL. |
| GET | `/eventos` | Consulta los eventos almacenados. |

## Instalación

1. Clona el repositorio.
2. Crea y activa un entorno virtual.
3. Instala las dependencias:

```bash
python -m pip install fastapi sqlalchemy "psycopg[binary]" python-dotenv pytest httpx uvicorn
```

4. Crea un archivo `.env` en la raíz del proyecto:

```text
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA
DB_HOST=localhost
DB_PORT=5432
DB_NAME=validador_eventos
```

5. Crea la base de datos `validador_eventos` en PostgreSQL.
6. Ejecuta la creación de tablas:

```bash
python crear_tablas.py
```

## Ejecución

Inicia el servidor con:

```bash
python -m uvicorn api:app --reload
```

Abre la documentación interactiva en:

`http://127.0.0.1:8000/docs`

## Pruebas automatizadas

Ejecuta todas las pruebas con:

```bash
python -m pytest -v
```

Las pruebas de la API utilizan una base SQLite temporal para evitar modificar los datos de la base PostgreSQL real.

## Objetivo del proyecto

Proyecto de portafolio para demostrar habilidades en desarrollo backend con Python, diseño de API REST, persistencia de datos, validación de información y pruebas automatizadas.