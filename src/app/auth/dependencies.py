"""
Dependencias de autenticación para FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.auth.jwt_handler import jwt_handler
import logging

logger = logging.getLogger(__name__)

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual a partir del token JWT
    
    Args:
        credentials: Credenciales del header Authorization
        db: Sesión de base de datos
        
    Returns:
        User: Usuario actual
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        payload = jwt_handler.verify_token(credentials.credentials)
        
        if payload is None:
            logger.warning("Token inválido o expirado")
            raise credentials_exception
        
        # Extraer información del usuario del token
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token sin información de usuario")
            raise credentials_exception
        
        # Buscar usuario en la base de datos
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if user is None:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            raise credentials_exception
        
        if not user.is_active:
            logger.warning(f"Usuario {user.username} está inactivo")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        return user
        
    except ValueError:
        logger.warning("ID de usuario inválido en token")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtiene el usuario actual activo
    
    Args:
        current_user: Usuario actual obtenido de get_current_user
        
    Returns:
        User: Usuario activo
        
    Raises:
        HTTPException: Si el usuario no está activo
    """
    if not current_user.is_active:
        logger.warning(f"Intento de acceso de usuario inactivo: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Obtiene el usuario actual que debe ser administrador
    
    Args:
        current_user: Usuario actual activo
        
    Returns:
        User: Usuario administrador
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if not current_user.is_admin:
        logger.warning(f"Intento de acceso admin de usuario no-admin: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos de administrador requeridos"
        )
    
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtiene el usuario actual si hay token, None si no
    
    Args:
        credentials: Credenciales opcionales
        db: Sesión de base de datos
        
    Returns:
        Optional[User]: Usuario actual o None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_permissions(required_permissions: list[str]):
    """
    Decorador para requerir permisos específicos
    
    Args:
        required_permissions: Lista de permisos requeridos
        
    Returns:
        Dependencia de FastAPI
    """
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        # Por ahora, solo verificamos si es admin
        # En el futuro se puede implementar un sistema de permisos más granular
        if not current_user.is_admin:
            user_permissions = []  # TODO: Implementar permisos de usuario
            if not any(perm in user_permissions for perm in required_permissions):
                logger.warning(f"Usuario {current_user.username} sin permisos: {required_permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permisos requeridos: {', '.join(required_permissions)}"
                )
        
        return current_user
    
    return permission_checker


def require_owner_or_admin(resource_user_id: int):
    """
    Requiere que el usuario sea el propietario del recurso o admin
    
    Args:
        resource_user_id: ID del usuario propietario del recurso
        
    Returns:
        Dependencia de FastAPI
    """
    async def owner_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.id != resource_user_id and not current_user.is_admin:
            logger.warning(f"Usuario {current_user.username} intentando acceder a recurso de usuario {resource_user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el propietario o un administrador pueden acceder a este recurso"
            )
        
        return current_user
    
    return owner_checker
