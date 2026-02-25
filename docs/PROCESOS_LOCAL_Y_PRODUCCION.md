# Procesos: modo local y producción

Resumen de comandos, variables y checklist para desarrollo local y despliegue en producción.

---

## Modo local

| Acción | Comando | Notas |
|--------|---------|--------|
| **Levantar todo (Docker)** | `docker-compose up -d` | API :8006, frontend :3001, postgres :5434, redis :6380 |
| **Ver logs** | `docker-compose logs -f app` | Backend en tiempo real |
| **Parar** | `docker-compose down` | Mantiene volúmenes (DB, redis) |
| **Backend sin Docker** | `scripts\run-local-backend.bat` o `./scripts/run-local-backend.sh` | Requiere `.env`; DB/Redis en Docker o local |
| **Frontend sin Docker** | `scripts\run-local-frontend.bat` o `./scripts/run-local-frontend.sh` | `REACT_APP_API_URL` en `frontend/.env` (ej. `http://localhost:8005`) |
| **Tests** | `pytest tests/ -v` | Con `TEST_SQLITE=1` para SQLite en memoria |
| **Migraciones** | `alembic upgrade head` | Desde raíz, con `.env` cargado |

### Variables clave (local)

- `DATABASE_URL`, `REDIS_HOST`, `REDIS_PORT` (o `REDIS_URL`) según tengas DB/Redis en Docker o local.
- `SECRET_KEY`: puede ser el de desarrollo; en prod **debe** cambiarse.
- `ENVIRONMENT=development`, `DEBUG=True`.

---

## Producción

| Acción | Comando | Notas |
|--------|---------|--------|
| **Levantar stack** | `docker-compose -f docker-compose.prod.yml up -d` | Definir `SECRET_KEY` y `POSTGRES_PASSWORD` (export o `--env-file .env.prod`) |
| **Con frontend** | `docker-compose -f docker-compose.prod.yml --profile frontend up -d` | Incluye servicio frontend en :3001 |
| **Migraciones** | Ejecutar antes o en el pipeline: `alembic upgrade head` | Contra la misma DB que usa la app (en contenedor o host) |
| **Health** | `GET /health` | Usado por el healthcheck de Docker y por balanceadores |

### Variables clave (producción)

- `ENVIRONMENT=production`, `DEBUG=False`.
- `SECRET_KEY`: **obligatorio** y distinto del valor por defecto (validado al arranque).
- `CORS_ORIGINS`: orígenes concretos (ej. `https://tu-dominio.com`), no `*`.
- `DATABASE_URL` y contraseñas desde secretos o archivo no versionado.

### Checklist pre-producción

- [ ] `SECRET_KEY` seguro (≥32 caracteres).
- [ ] `ENVIRONMENT=production`, `DEBUG=False`.
- [ ] CORS con dominios reales.
- [ ] Migraciones aplicadas.
- [ ] Frontend construido con `REACT_APP_API_URL` correcto (vacío si mismo origen vía proxy).
- [ ] Health check respondiendo (`/health`).

---

## Diferencias rápidas

| Aspecto | Local | Producción |
|---------|--------|------------|
| Compose | `docker-compose.yml` (Dockerfile.dev) | `docker-compose.prod.yml` (Dockerfile) |
| Docs API | `/docs` y `/redoc` activos | Desactivados por defecto (ver nota abajo) |
| Hot reload | Sí (dev) | No |
| Healthcheck | 15s intervalo, 20s start_period | 30s intervalo, 40s start_period |
| Workers | 1 | 2 réplicas (prod) |

**Nota**: En producción las rutas `/docs`, `/redoc` y `/openapi.json` están deshabilitadas por seguridad. Si las necesitas (ej. documentación interna), se pueden habilitar condicionadas por variable de entorno; ver `src/app/main.py` (`create_app`).

---

Para más detalle: **MANUAL_DESARROLLADOR.md** (configuración, tests, API) y **MANUAL_USUARIO.md** (uso del sistema).
