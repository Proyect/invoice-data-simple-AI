"""
Rutas de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Union
import logging

from ..core.database import get_db
from ..models.user import User
from ..schemas.auth import (
    UserCreate, UserResponse, UserLogin, TokenResponse, 
    RefreshTokenRequest, ChangePasswordRequest, MessageResponse,
    UserUpdate
)
from ..auth.password_handler import PasswordHandler
from ..auth.jwt_handler import jwt_handler
from ..auth.dependencies import get_current_active_user, get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario
    
    Args:
        user_data: Datos del usuario a registrar
        db: Sesión de base de datos
        
    Returns:
        UserResponse: Usuario creado
        
    Raises:
        HTTPException: Si el usuario ya existe o hay error en la creación
    """
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
        
        # Crear hash de la contraseña
        hashed_password = PasswordHandler.get_password_hash(user_data.password)
        
        # Crear usuario
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Usuario registrado exitosamente: {db_user.username} ({db_user.email})")
        
        return UserResponse.from_orm(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registrando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al registrar usuario"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y retorna tokens JWT
    
    Args:
        form_data: Datos del formulario de login (username, password)
        db: Sesión de base de datos
        
    Returns:
        TokenResponse: Tokens de acceso y refresco
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    try:
        # Buscar usuario por username o email
        user = db.query(User).filter(
            (User.username == form_data.username) | (User.email == form_data.username)
        ).first()
        
        if not user:
            logger.warning(f"Intento de login con usuario inexistente: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar contraseña
        if not PasswordHandler.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Intento de login con contraseña incorrecta para usuario: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            logger.warning(f"Intento de login de usuario inactivo: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Crear tokens
        user_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin
        }
        
        access_token = jwt_handler.create_access_token(user_data)
        refresh_token = jwt_handler.create_refresh_token(user_data)
        
        logger.info(f"Login exitoso para usuario: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60  # 30 minutos en segundos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresca un token de acceso usando un token de refresco
    
    Args:
        refresh_data: Token de refresco
        db: Sesión de base de datos
        
    Returns:
        TokenResponse: Nuevo token de acceso
        
    Raises:
        HTTPException: Si el token de refresco es inválido
    """
    try:
        # Verificar token de refresco
        payload = jwt_handler.verify_token(refresh_data.refresh_token, token_type="refresh")
        
        if not payload:
            logger.warning("Intento de refresh con token inválido")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido o expirado"
            )
        
        # Verificar que el usuario aún existe y está activo
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            logger.warning(f"Token de refresco para usuario inexistente o inactivo: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Crear nuevo token de acceso
        user_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin
        }
        
        new_access_token = jwt_handler.create_access_token(user_data)
        
        logger.info(f"Token refrescado para usuario: {user.username}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_data.refresh_token,  # El refresh token sigue siendo válido
            expires_in=30 * 60  # 30 minutos en segundos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refrescando token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene información del usuario actual
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        UserResponse: Información del usuario
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza información del usuario actual
    
    Args:
        user_update: Datos a actualizar
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        UserResponse: Usuario actualizado
    """
    try:
        # Verificar si el email o username ya están en uso por otro usuario
        if user_update.email:
            existing_user = db.query(User).filter(
                User.email == user_update.email,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso por otro usuario"
                )
        
        if user_update.username:
            existing_user = db.query(User).filter(
                User.username == user_update.username,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
        
        # Actualizar campos
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Usuario actualizado: {current_user.username}")
        
        return UserResponse.from_orm(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual
    
    Args:
        password_data: Datos para cambiar contraseña
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        MessageResponse: Mensaje de confirmación
    """
    try:
        # Verificar contraseña actual
        if not PasswordHandler.verify_password(password_data.current_password, current_user.hashed_password):
            logger.warning(f"Intento de cambio de contraseña con contraseña incorrecta para usuario: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña
        current_user.hashed_password = PasswordHandler.get_password_hash(password_data.new_password)
        db.commit()
        
        logger.info(f"Contraseña cambiada para usuario: {current_user.username}")
        
        return MessageResponse(message="Contraseña cambiada exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cambiando contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los usuarios (solo administradores)
    
    Args:
        skip: Número de usuarios a omitir
        limit: Número máximo de usuarios a retornar
        current_user: Usuario administrador actual
        db: Sesión de base de datos
        
    Returns:
        list[UserResponse]: Lista de usuarios
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.from_orm(user) for user in users]
        
    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

