#!/usr/bin/env python3
"""
Script para actualizar contraseña del usuario administrador
"""

import os
import sys
from pathlib import Path

# Configurar SQLite para desarrollo
os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.core.database import SessionLocal
from app.models.user import User
from app.auth.password_handler import PasswordHandler

def update_admin_password():
    """Actualizar contraseña del usuario administrador"""
    
    db = SessionLocal()
    
    try:
        # Buscar usuario administrador
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("No se encontró el usuario administrador")
            return
        
        # Actualizar contraseña
        password_handler = PasswordHandler()
        new_password = "Admin123!"
        admin_user.hashed_password = password_handler.get_password_hash(new_password)
        
        db.commit()
        
        print("Contraseña del usuario administrador actualizada exitosamente!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Nueva Password: {new_password}")
        
    except Exception as e:
        print(f"Error actualizando contraseña: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Actualizando contraseña del usuario administrador...")
    update_admin_password()
    print("Proceso completado!")







