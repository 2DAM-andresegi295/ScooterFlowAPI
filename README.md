# ScooterFlowAPI

## Descripción
API para la gestión de patinetes eléctricos y zonas de operación, desarrollada con FastAPI, PostgreSQL, SQLAlchemy y Alembic. Incluye infraestructura Docker y CI con GitHub Actions.

## Levantar el proyecto en un solo comando

```powershell
docker compose up -d --build
```

Esto levanta `db` y `api`. El servicio `api` espera a que PostgreSQL esté sano y ejecuta `alembic upgrade head` antes de iniciar FastAPI.

Una vez arriba, la documentación queda disponible en:
- `http://localhost:8000/docs`

## Migraciones

Para aplicar las migraciones manualmente dentro del contenedor de la API:

```powershell
docker compose exec api alembic upgrade head
```

## Ejecutar tests

Los tests usan una base SQLite aislada para ejecutarse de forma reproducible y sin depender de servicios externos.

```powershell
$env:PYTHONPATH = "D:\ScooterFlowAPI"
pytest app/test_main.py -q
```

## CI/CD

Cada `push` a la rama `main` levanta PostgreSQL en GitHub Actions, aplica las migraciones con Alembic y ejecuta los tests con `pytest`.

## Estructura del proyecto
- `app/`: código fuente de la API
- `migrations/`: historial de migraciones Alembic
- `.github/workflows/`: workflow de CI
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`

## Autor
ScooterFlow DevOps
