#!/usr/bin/env python3
"""
Script completo para probar todos los endpoints con base de datos
"""
import requests
import json

BASE_URL = "http://localhost:8002"

def test_endpoint(method, endpoint, expected_status=200, data=None):
    """Probar un endpoint"""
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method.upper() == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        status_ok = response.status_code == expected_status
        status_icon = "[PASS]" if status_ok else "[FAIL]"
        
        print(f"{status_icon} {method} {endpoint}")
        print(f"   Status: {response.status_code} (expected: {expected_status})")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "total" in data:
                    print(f"   Total items: {data['total']}")
                elif isinstance(data, dict) and "message" in data:
                    print(f"   Message: {data['message']}")
                else:
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Error: {response.text}")
        
        print()
        return status_ok
        
    except Exception as e:
        print(f"[FAIL] {method} {endpoint}")
        print(f"   Error: {e}")
        print()
        return False

def main():
    print("PROBANDO ENDPOINTS CON BASE DE DATOS")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Endpoint raíz
    tests.append(test_endpoint("GET", "/", 200))
    
    # Test 2: Endpoint de prueba
    tests.append(test_endpoint("GET", "/test", 200))
    
    # Test 3: Listar documentos
    tests.append(test_endpoint("GET", "/api/v2/documents/", 200))
    
    # Test 4: Obtener documento específico
    tests.append(test_endpoint("GET", "/api/v2/documents/1", 200))
    
    # Test 5: Obtener documento que no existe
    tests.append(test_endpoint("GET", "/api/v2/documents/999", 200))  # Esperamos 200 pero con error en el contenido
    
    # Test 6: Crear documento
    document_data = {
        "filename": "test_document.pdf",
        "document_type": "factura",
        "status": "pending",
        "confidence_score": 0.0
    }
    tests.append(test_endpoint("POST", "/api/v2/documents/", 200, document_data))
    
    # Test 7: Listar documentos después de crear
    tests.append(test_endpoint("GET", "/api/v2/documents/", 200))
    
    # Test 8: Estadísticas
    tests.append(test_endpoint("GET", "/api/v2/documents/stats/overview", 200))
    
    # Resumen
    passed = sum(tests)
    total = len(tests)
    
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"Total de tests: {total}")
    print(f"Pasaron: {passed}")
    print(f"Fallaron: {total - passed}")
    print(f"Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\nCONCLUSION: ¡Todos los endpoints funcionan correctamente!")
    else:
        print("\nCONCLUSION: Algunos endpoints necesitan ajustes")

if __name__ == "__main__":
    main()
