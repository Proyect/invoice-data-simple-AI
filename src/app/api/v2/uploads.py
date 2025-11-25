"""
Upload Endpoints v2
===================

Endpoints optimizados para subida de documentos.
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def upload_document():
    """Endpoint de subida - en desarrollo"""
    return {"message": "Upload endpoint v2 - en desarrollo"}

