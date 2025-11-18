#!/usr/bin/env python3
"""
Test Simplificado de Producción
===============================

Script simple para probar sistema en producción.
"""

import requests

def test_production():
    """Probar sistema de producción"""
    base_url = "http://localhost:8005"
    
    print("=== TEST PRODUCCIÓN ===")
    
    # Tests básicos
    tests = [
        ("/", "Servidor principal"),
        ("/health", "Health check"),
        ("/documents", "Lista documentos"),
        ("/documents/stats", "Estadísticas"),
    ]
    
    success = 0
    total = len(tests)
    
    for endpoint, name in tests:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401, 422]:
                print(f"✅ {name}: OK")
                success += 1
            else:
                print(f"❌ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print(f"\n📊 Resultado: {success}/{total} tests exitosos")
    
    if success == total:
        print("🎉 Sistema de producción funcionando correctamente!")
    else:
        print("⚠️  Algunos tests fallaron")
    
    return success == total

if __name__ == "__main__":
    test_production()





