"""
Script de inicio simplificado para la aplicación
"""
import uvicorn
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print(f"Iniciando {settings.APP_NAME}")
    print(f"Puerto: {settings.PORT}")
    print(f"Debug: {settings.DEBUG}")
    print("=" * 60)
    print(f"Documentacion: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Health check: http://{settings.HOST}:{settings.PORT}/health")
    print(f"API principal: http://{settings.HOST}:{settings.PORT}/api/v1/upload")
    print("=" * 60)
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )



