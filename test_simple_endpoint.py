#!/usr/bin/env python3
"""
Test Simplificado de Endpoint
=============================

Script simple para probar un endpoint básico.
"""

import requests

def test_endpoint():
    """Probar endpoint básico"""
    url = "http://localhost:8005/"
    
    print("=== TEST ENDPOINT BÁSICO ===")
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando")
            print(f"📄 Respuesta: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_endpoint()