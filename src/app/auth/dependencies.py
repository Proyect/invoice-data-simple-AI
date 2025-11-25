"""
Dependencias de autenticación para FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..models.user import User
from .jwt_handler import jwt_handler
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
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token sin información de usuario")
            raise credentials_exception
        
        # Buscar usuario en la base de datos por username
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            logger.warning(f"Usuario con username {username} no encontrado")
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


def get_user_permissions(user: User) -> list[str]:
    """
    Obtener permisos del usuario basados en su rol y configuración
    
    Args:
        user: Usuario
        
    Returns:
        Lista de permisos del usuario
    """
    permissions = []
    
    # Admins tienen todos los permisos
    if user.is_admin:
        return ["*"]  # "*" significa todos los permisos
    
    # Permisos básicos para todos los usuarios activos
    if user.is_active:
        permissions.extend([
            "documents:read",
            "documents:create",
            "documents:update:own",
            "documents:delete:own"
        ])
    
    # Si el usuario está verificado, tiene permisos adicionales
    if user.is_verified:
        permissions.extend([
            "documents:export",
            "documents:share"
        ])
    
    # Leer permisos adicionales desde profile_data si existe
    if user.profile_data:
        try:
            import json
            profile = json.loads(user.profile_data)
            if isinstance(profile, dict):
                additional_permissions = profile.get("permissions", [])
                if isinstance(additional_permissions, list):
                    permissions.extend(additional_permissions)
        except Exception as e:
            logger.warning(f"Error parseando permisos de profile_data para usuario {user.username}: {e}")
    
    return list(set(permissions))  # Eliminar duplicados


def require_permissions(required_permissions: list[str]):
    """
    Decorador para requerir permisos específicos
    
    Args:
        required_permissions: Lista de permisos requeridos
        
    Returns:
        Dependencia de FastAPI
    """
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        user_permissions = get_user_permissions(current_user)
        
        # Si el usuario tiene permiso "*", tiene todos los permisos
        if "*" in user_permissions:
            return current_user
        
        # Verificar si el usuario tiene todos los permisos requeridos
        missing_permissions = [
            perm for perm in required_permissions
            if perm not in user_permissions
        ]
        
        if missing_permissions:
            logger.warning(
                f"Usuario {current_user.username} sin permisos requeridos: {missing_permissions}. "
                f"Permisos del usuario: {user_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos requeridos: {', '.join(missing_permissions)}"
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

