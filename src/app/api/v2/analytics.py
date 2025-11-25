"""
Analytics Endpoints v2
======================

Endpoints para análisis y estadísticas.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_analytics():
    """Estadísticas - en desarrollo"""
    return {"message": "Analytics endpoint v2 - en desarrollo"}

