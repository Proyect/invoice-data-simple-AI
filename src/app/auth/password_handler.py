"""
Manejo seguro de contraseñas usando bcrypt
"""
from passlib.context import CryptContext
import re
from typing import Tuple, Optional

# Configurar bcrypt para hashing seguro
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHandler:
    """Manejo seguro de contraseñas"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica una contraseña contra su hash
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash de la contraseña
            
        Returns:
            bool: True si la contraseña es correcta
        """
        # Si es un hash bcrypt, usar bcrypt
        if hashed_password.startswith('$2b$'):
            return pwd_context.verify(plain_password, hashed_password)
        
        # Si es un hash SHA256, usar SHA256
        import hashlib
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Genera un hash seguro de la contraseña
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
        """
        Valida la fortaleza de una contraseña
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valida, mensaje_error)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if len(password) > 128:
            return False, "La contraseña no puede tener más de 128 caracteres"
        
        # Verificar que tenga al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        # Verificar que tenga al menos una letra mayúscula
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        # Verificar que tenga al menos un número
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        # Verificar que tenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>)"
        
        # Verificar que no contenga espacios
        if ' ' in password:
            return False, "La contraseña no puede contener espacios"
        
        return True, None
    
    @staticmethod
    def generate_secure_password() -> str:
        """
        Genera una contraseña segura aleatoria
        
        Returns:
            str: Contraseña segura generada
        """
        import secrets
        import string
        
        # Definir caracteres permitidos
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        
        # Asegurar al menos un carácter de cada tipo
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special_chars)
        ]
        
        # Completar con caracteres aleatorios
        all_chars = lowercase + uppercase + digits + special_chars
        for _ in range(12):  # Total de 16 caracteres
            password.append(secrets.choice(all_chars))
        
        # Mezclar la lista
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
