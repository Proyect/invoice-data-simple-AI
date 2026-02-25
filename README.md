# Document Extractor API

Sistema de extracción y análisis de documentos con IA, OCR híbrido y procesamiento asíncrono.

## Documentación

- **[Manual del usuario](MANUAL_USUARIO.md)** — Uso del sistema, configuración, API, Docker y solución de problemas.
- **[Manual del desarrollador](MANUAL_DESARROLLADOR.md)** — Arquitectura, desarrollo local, tests, migraciones y buenas prácticas.
- **[Procesos local y producción](docs/PROCESOS_LOCAL_Y_PRODUCCION.md)** — Comandos, variables y checklist para local y producción.
- **[Changelog](CHANGELOG.md)** — Historial de cambios.

## Inicio rápido

```bash
# Con Docker
docker-compose up -d
# API: http://localhost:8006  |  Docs: http://localhost:8006/docs  |  Frontend: http://localhost:3001

# Local
pip install -r requirements.txt
cp env.example .env
python main.py
# http://localhost:8005/docs
```

---

Licencia MIT
