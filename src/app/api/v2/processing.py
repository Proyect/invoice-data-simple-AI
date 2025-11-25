"""
Processing Endpoints v2
========================

Endpoints para procesamiento de documentos.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_processing_status():
    """Estado de procesamiento - en desarrollo"""
    return {"message": "Processing endpoint v2 - en desarrollo"}

