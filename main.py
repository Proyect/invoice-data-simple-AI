import uvicorn
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Iniciando {settings.APP_NAME} en puerto {settings.PORT}")
    print(f"📖 Documentación disponible en: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 Health check en: http://{settings.HOST}:{settings.PORT}/health")
    print(f"ℹ️  Información del sistema en: http://{settings.HOST}:{settings.PORT}/info")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
