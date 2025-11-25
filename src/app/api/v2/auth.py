"""
Authentication Endpoints v2
===========================

Endpoints para autenticación.
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    """Login - en desarrollo"""
    return {"message": "Auth endpoint v2 - en desarrollo"}

