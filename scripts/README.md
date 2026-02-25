# Scripts de desarrollo y despliegue

## Modo local (sin Docker)

- **run-local-backend.bat** / **run-local-backend.sh**: inician el backend con uvicorn (hot-reload). Requieren `.env` en la raíz (copiar desde `env.example`). Base de datos y Redis según `DATABASE_URL` y `REDIS_*` (si usas solo Docker para postgres/redis, deja las URLs apuntando a localhost con los puertos mapeados).
- **run-local-frontend.bat** / **run-local-frontend.sh**: inician el frontend en modo desarrollo. Crean `frontend/.env` desde `frontend/env.example` si no existe. El frontend por defecto llama a la API en `http://localhost:8006`; si el backend corre en 8005, en `frontend/.env` pon `REACT_APP_API_URL=http://localhost:8005`.

## Con Docker

- **Desarrollo**: desde la raíz, `docker-compose up -d`. API en 8006, frontend en 3001.
- **Producción**: `docker-compose -f docker-compose.prod.yml up -d`. Definir `SECRET_KEY` y `POSTGRES_PASSWORD` (export o archivo `.env.prod` con `--env-file .env.prod`). Ver **MANUAL_DESARROLLADOR.md** sección "Modo local vs producción".
