# Rutas Legacy - DEPRECATED

⚠️ **ADVERTENCIA**: Este módulo está DEPRECADO.

Las rutas en este módulo están siendo migradas a API v2 (`src/app/api/v2/`).

## Estado de Migración

- ✅ **Migrado a API v2**: Funcionalidad principal disponible en `/api/v2/`
- ⚠️ **Mantenido temporalmente**: Estas rutas se mantienen para compatibilidad con código existente
- 🔄 **En proceso**: Algunas rutas aún están siendo migradas

## Rutas Disponibles

### API v1 (Legacy)
- `/api/v1/upload` - Subida de documentos
- `/api/v1/documents` - Gestión de documentos
- `/api/v1/health` - Health check

### API v2 (Actual - Recomendado)
- `/api/v2/uploads/` - Subida de documentos optimizada
- `/api/v2/documents/` - Gestión de documentos mejorada
- `/api/v2/processing/` - Procesamiento asíncrono
- `/api/v2/analytics/` - Analytics y métricas
- `/api/v2/auth/` - Autenticación mejorada

## Migración

Para migrar código que usa estas rutas:

1. Revisa la documentación en `docs/ROUTES_MIGRATION_GUIDE.md`
2. Actualiza los endpoints a `/api/v2/`
3. Verifica que los schemas y respuestas sean compatibles

## Eliminación Futura

Estas rutas legacy serán eliminadas en una versión futura (v3.0.0). Se recomienda migrar cuanto antes.













