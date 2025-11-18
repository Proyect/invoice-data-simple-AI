#!/usr/bin/env python3
"""
Test del Sistema de Producción
==============================

Script para probar los componentes principales del sistema en producción.
"""
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def test_system(base_url: str = "http://localhost:8005") -> bool:
    """Probar sistema básico"""
    print("=== TEST SISTEMA DE PRODUCCIÓN ===")
    print(f"URL: {base_url}")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Servidor funcionando
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            tests_passed += 1
        else:
            print(f"❌ Servidor error: {response.status_code}")
    except Exception as e:
        print(f"❌ No se puede conectar: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check OK")
            tests_passed += 1
        else:
            print(f"⚠️  Health check: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Health check error: {e}")
    
    # Test 3: Documentos
    try:
        response = requests.get(f"{base_url}/api/v2/documents/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documentos: {data.get('total', 0)} encontrados")
            tests_passed += 1
        else:
            print(f"⚠️  Documentos: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Documentos error: {e}")
    
    # Test 4: Estadísticas
    try:
        response = requests.get(f"{base_url}/api/v2/documents/stats/overview", timeout=5)
        if response.status_code == 200:
            print("✅ Estadísticas OK")
            tests_passed += 1
        else:
            print(f"⚠️  Estadísticas: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Estadísticas error: {e}")
    
    print(f"\n🎉 Test completado! {tests_passed}/{total_tests} pruebas pasaron")
    return tests_passed == total_tests


def test_endpoints_detailed(base_url: str = "http://localhost:8005") -> Dict[str, Any]:
    """Probar endpoints con detalles"""
    results = {
        "base_url": base_url,
        "tests": {},
        "summary": {"passed": 0, "failed": 0, "total": 0}
    }
    
    endpoints = [
        ("/", "GET", "Root endpoint"),
        ("/health", "GET", "Health check"),
        ("/info", "GET", "System info"),
        ("/api/v2/documents/", "GET", "List documents"),
        ("/api/v2/documents/stats/overview", "GET", "Document stats"),
        ("/api/v2/documents/needing-review/", "GET", "Documents needing review"),
        ("/api/v2/documents/recent/", "GET", "Recent documents"),
        ("/api/v2/documents/high-confidence/", "GET", "High confidence documents"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            test_result = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "description": description
            }
            
            if response.status_code == 200:
                try:
                    test_result["data"] = response.json()
                except:
                    test_result["data"] = response.text
            
            results["tests"][endpoint] = test_result
            
            if test_result["success"]:
                results["summary"]["passed"] += 1
                print(f"✅ {description}: {response.status_code}")
            else:
                results["summary"]["failed"] += 1
                print(f"❌ {description}: {response.status_code}")
            
            results["summary"]["total"] += 1
            
        except Exception as e:
            results["tests"][endpoint] = {
                "status_code": None,
                "success": False,
                "error": str(e),
                "description": description
            }
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
            print(f"❌ {description}: Error - {e}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        results = test_endpoints_detailed()
        print(f"\n📊 Resumen: {results['summary']['passed']}/{results['summary']['total']} pruebas pasaron")
    else:
        success = test_system()
        sys.exit(0 if success else 1)





