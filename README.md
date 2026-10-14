# Validador de Eventos API

API REST desarrollada en Python para validar, registrar y consultar eventos. Permite validar fechas y campos obligatorios, detectar identificadores duplicados, procesar archivos CSV y almacenar eventos en PostgreSQL.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Psycopg
- Pytest
- SQLite en memoria para pruebas automatizadas

## Funcionalidades

- Validación de campos obligatorios.
- Validación de fechas.
- Detección de identificadores duplicados.
- Carga y exportación de datos CSV.
- Registro de eventos en PostgreSQL.
- Consulta de eventos almacenados.
- Manejo de errores mediante códigos HTTP.
- Restricción `UNIQUE` en PostgreSQL para evitar identificadores duplicados.
- Pruebas automatizadas de validaciones, archivos y API.

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Comprueba que la API está disponible. |
| POST | `/eventos/validar` | Valida una lista de eventos. |
| POST | `/eventos` | Registra un evento en PostgreSQL. |
| GET | `/eventos` | Consulta los eventos almacenados. |

### Códigos HTTP principales

- `200 OK`: consulta o validación exitosa.
- `201 Created`: evento creado correctamente.
- `409 Conflict`: el identificador del evento ya existe.
- `422 Unprocessable Content`: los datos enviados no superan la validación.
- `503 Service Unavailable`: el servicio de almacenamiento no está disponible.

## Requisitos previos

- Python 3.11 o superior.
- PostgreSQL instalado y en ejecución.
- Git para clonar el repositorio.

## Instalación en Windows

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Adr526/Validador_datos_phyton.git
cd Validador_datos_phyton
```

### 2. Crear el entorno virtual

```powershell
python -m venv .venv
```

### 3. Instalar las dependencias

No es obligatorio activar el entorno virtual para ejecutar Python desde él directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```text
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA
DB_HOST=localhost
DB_PORT=5432
DB_NAME=validador_eventos
```

Reemplaza `TU_CONTRASEÑA` por la contraseña de tu usuario de PostgreSQL.

**No publiques el archivo `.env` ni compartas tus credenciales.** Este archivo está excluido del repositorio mediante `.gitignore`.

### 5. Crear la base de datos

Crea una base de datos llamada `validador_eventos` en PostgreSQL.

Después, desde la carpeta del proyecto, ejecuta:

```powershell
.\.venv\Scripts\python.exe crear_tablas.py
```

## Ejecutar la API

Inicia el servidor:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

La API estará disponible en:

`http://127.0.0.1:8000`

La documentación interactiva se encuentra en:

`http://127.0.0.1:8000/docs`

Para detener el servidor, pulsa `Ctrl + C` en la terminal.

## Pruebas automatizadas

Ejecuta todas las pruebas con:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Las pruebas de la API utilizan una base de datos SQLite temporal para evitar modificar los datos de PostgreSQL utilizados por la aplicación.

## Estructura principal del proyecto

- `api.py`: endpoints y manejo de solicitudes HTTP.
- `validaciones.py`: reglas de validación de eventos.
- `archivos.py`: importación y exportación de archivos CSV.
- `modelos.py`: modelo de datos de SQLAlchemy.
- `esquemas.py`: esquemas de entrada y salida de la API.
- `operaciones_eventos.py`: operaciones de persistencia y manejo de errores.
- `database.py`: conexión y sesiones de base de datos.
- `configuracion.py`: configuración de la conexión.
- `crear_tablas.py`: creación de tablas.
- `test_validaciones.py`: pruebas de las validaciones.
- `test_archivos.py`: pruebas de los archivos CSV.
- `test_api.py`: pruebas generales de la API.
- `test_api_db.py`: pruebas de la API con una base de datos temporal.
- `requirements.txt`: dependencias del proyecto.

## Objetivo del proyecto

Proyecto de portafolio orientado a demostrar habilidades en desarrollo backend con Python, diseño de API REST, persistencia de datos, validación de información y pruebas automatizadas.