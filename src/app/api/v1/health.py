"""
Health Endpoints v1 (Legacy)
=============================

Endpoints legacy para compatibilidad.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    """Health check legacy"""
    return {"status": "ok", "version": "v1"}

