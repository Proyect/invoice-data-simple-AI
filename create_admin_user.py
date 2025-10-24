#!/usr/bin/env python3
"""
Script para crear usuario administrador inicial
==============================================

Este script crea un usuario administrador por defecto en el sistema.
Se ejecuta una sola vez durante la configuración inicial.
"""

import os
import sys
from pathlib import Path

# Configurar SQLite para desarrollo
os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.auth.password_handler import PasswordHandler
from app.core.config import settings

def create_admin_user():
    """Crear usuario administrador inicial"""
    
    # Crear tablas si no existen
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        
        if existing_admin:
            print(f"Ya existe un usuario administrador: {existing_admin.username}")
            return
        
        # Crear usuario administrador
        password_handler = PasswordHandler()
        admin_password = "Admin123!"
        admin_user = User(
            email="admin@documentextractor.com",
            username="admin",
            hashed_password=password_handler.get_password_hash(admin_password),
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("Usuario administrador creado exitosamente!")
        print(f"   Username: admin")
        print(f"   Email: admin@documentextractor.com")
        print(f"   Password: {admin_password}")
        print(f"   ID: {admin_user.id}")
        print("\nIMPORTANTE: Cambia la contraseña después del primer login!")
        
    except Exception as e:
        print(f"Error creando usuario administrador: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Creando usuario administrador inicial...")
    create_admin_user()
    print("Proceso completado!")
