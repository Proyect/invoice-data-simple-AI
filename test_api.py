"""
Script de prueba para verificar que la API funciona con PostgreSQL
"""
import requests
import os
from pathlib import Path

# Configuración
API_URL = "http://localhost:8005"
TEST_FILE = Path("uploads/test_invoice.jpg")

def test_health():
    """Probar health check"""
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check falló: {e}")
        return False

def test_upload():
    """Probar upload de documento"""
    if not TEST_FILE.exists():
        print(f"❌ Archivo de prueba no existe: {TEST_FILE}")
        return False
    
    try:
        with open(TEST_FILE, "rb") as f:
            files = {"file": (TEST_FILE.name, f, "image/jpeg")}
            data = {"document_type": "factura"}
            
            response = requests.post(
                f"{API_URL}/api/v1/upload",
                files=files,
                data=data
            )
            
            print(f"✅ Upload: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Document ID: {result.get('document_id')}")
                print(f"   Confidence: {result.get('confidence')}")
                print(f"   Datos extraídos: {list(result.get('extracted_data', {}).keys())}")
                return True
            else:
                print(f"   Error: {response.json()}")
                return False
                
    except Exception as e:
        print(f"❌ Upload falló: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Test de API con PostgreSQL")
    print("=" * 50)
    
    # Esperar a que el servidor esté listo
    import time
    print("\n⏳ Esperando a que el servidor esté listo...")
    time.sleep(3)
    
    # Pruebas
    health_ok = test_health()
    print()
    
    if health_ok:
        upload_ok = test_upload()
        print()
        
        if upload_ok:
            print("=" * 50)
            print("✅ TODAS LAS PRUEBAS PASARON")
            print("=" * 50)
        else:
            print("=" * 50)
            print("❌ UPLOAD FALLÓ")
            print("=" * 50)
    else:
        print("=" * 50)
        print("❌ SERVIDOR NO ESTÁ CORRIENDO")
        print("=" * 50)

