"""
Manejo de tokens JWT para autenticación
"""
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """Manejo de tokens JWT"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Crea un token de acceso JWT
        
        Args:
            data: Datos a incluir en el token (ej: {"sub": user_id, "email": email})
            
        Returns:
            str: Token JWT codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token de acceso creado para usuario: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creando token de acceso: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al crear token"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Crea un token de refresco JWT
        
        Args:
            data: Datos a incluir en el token
            
        Returns:
            str: Token JWT de refresco codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token de refresco creado para usuario: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creando token de refresco: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al crear token de refresco"
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            token_type: Tipo de token esperado ("access" o "refresh")
            
        Returns:
            Optional[Dict[str, Any]]: Payload del token si es válido, None si no
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                logger.warning(f"Token tipo incorrecto. Esperado: {token_type}, Recibido: {payload.get('type')}")
                return None
            
            # Verificar expiración (jose lo hace automáticamente, pero por seguridad)
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token expirado")
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning(f"Error verificando token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado verificando token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Crea un nuevo token de acceso usando un token de refresco válido
        
        Args:
            refresh_token: Token de refresco
            
        Returns:
            Optional[str]: Nuevo token de acceso si el refresh token es válido
        """
        payload = self.verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            return None
        
        # Extraer datos del usuario del payload
        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "is_admin": payload.get("is_admin", False)
        }
        
        # Crear nuevo token de acceso
        return self.create_access_token(user_data)
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el payload de un token sin verificar expiración
        (Útil para debugging o análisis)
        
        Args:
            token: Token JWT
            
        Returns:
            Optional[Dict[str, Any]]: Payload del token
        """
        try:
            # Decodificar sin verificar expiración
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except JWTError as e:
            logger.warning(f"Error decodificando token: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Verifica si un token está expirado
        
        Args:
            token: Token JWT
            
        Returns:
            bool: True si el token está expirado
        """
        payload = self.get_token_payload(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.fromtimestamp(exp) < datetime.utcnow()


# Instancia global del manejador JWT
jwt_handler = JWTHandler()
