#!/usr/bin/env python3
"""
Test Simplificado de Registro de Routers
========================================

Script simple para verificar que los routers están registrados.
"""

import requests

def test_routers():
    """Probar routers registrados"""
    base_url = "http://localhost:8005"
    
    print("=== TEST ROUTERS ===")
    
    # Lista de endpoints a probar
    endpoints = [
        ("/", "GET", "Root"),
        ("/health", "GET", "Health"),
        ("/documents", "GET", "Documents"),
        ("/documents/stats", "GET", "Stats"),
        ("/upload/test", "GET", "Upload Test"),
    ]
    
    success = 0
    total = len(endpoints)
    
    for endpoint, method, name in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401, 422]:  # 401/422 son respuestas válidas
                print(f"✅ {name}: {response.status_code}")
                success += 1
            else:
                print(f"❌ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print(f"\n📊 Resultado: {success}/{total} routers funcionando")
    return success == total

if __name__ == "__main__":
    test_routers()