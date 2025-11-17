#!/usr/bin/env python3
"""
Script para crear usuario administrador con contraseña simple
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

def create_simple_admin():
    """Crear usuario administrador con contraseña simple"""
    
    db = SessionLocal()
    
    try:
        # Eliminar usuario admin existente
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            db.delete(existing_admin)
            db.commit()
        
        # Crear usuario administrador con contraseña simple
        password_handler = PasswordHandler()
        simple_password = "admin123"
        
        # Crear hash manualmente para evitar problemas de validación
        import hashlib
        simple_hash = hashlib.sha256(simple_password.encode()).hexdigest()
        
        admin_user = User(
            email="admin@documentextractor.com",
            username="admin",
            hashed_password=simple_hash,  # Usar hash simple temporalmente
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("Usuario administrador creado con contraseña simple!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: {simple_password}")
        print(f"   ID: {admin_user.id}")
        
    except Exception as e:
        print(f"Error creando usuario: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Creando usuario administrador con contraseña simple...")
    create_simple_admin()
    print("Proceso completado!")







