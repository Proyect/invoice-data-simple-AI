#!/usr/bin/env python3
"""
Test Simplificado de Base de Datos
=================================

Script simple para probar conexión y operaciones básicas de BD.
"""

import os
import sys
from pathlib import Path

# Configurar SQLite
os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"

# Agregar src al path (ahora estamos en tests/integration/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_database():
    """Probar base de datos"""
    print("=== TEST BASE DE DATOS ===")
    
    try:
        from app.core.database import engine, SessionLocal
        from app.models.document import Document
        
        # Test 1: Conexión
        print("🔌 Probando conexión...")
        with engine.connect() as conn:
            print("✅ Conexión exitosa")
        
        # Test 2: Sesión
        print("📊 Probando sesión...")
        db = SessionLocal()
        try:
            # Contar documentos
            count = db.query(Document).count()
            print(f"✅ Documentos en BD: {count}")
            
            # Listar últimos 3 documentos
            recent = db.query(Document).order_by(Document.created_at.desc()).limit(3).all()
            if recent:
                print("📄 Últimos documentos:")
                for doc in recent:
                    print(f"   - {doc.filename} (ID: {doc.id})")
            else:
                print("📄 No hay documentos")
                
        finally:
            db.close()
        
        print("🎉 Test de BD completado!")
        return True
        
    except Exception as e:
        print(f"❌ Error en BD: {e}")
        return False

if __name__ == "__main__":
    test_database()