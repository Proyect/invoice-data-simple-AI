"""
Routes Legacy - DEPRECATED
==========================

⚠️ ADVERTENCIA: Este módulo está DEPRECADO.

Las rutas en este módulo están siendo migradas a API v2.
Por favor, usa los endpoints de `/api/v2/` en su lugar.

Para más información sobre la migración, consulta:
- ROUTES_MIGRATION_GUIDE.md
- API v2: /api/v2/docs

Las rutas legacy se mantendrán temporalmente para compatibilidad,
pero serán removidas en una versión futura.
"""

import warnings

# Emitir advertencia al importar el módulo
warnings.warn(
    "El módulo 'routes' está deprecado. Por favor, usa '/api/v2/' en su lugar. "
    "Consulta ROUTES_MIGRATION_GUIDE.md para más información.",
    DeprecationWarning,
    stacklevel=2
)
