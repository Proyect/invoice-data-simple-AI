#!/usr/bin/env python3
"""
Script para probar las funcionalidades del frontend
"""

import requests
import json
import time

def test_api_endpoints():
    """Probar todos los endpoints de la API"""
    
    base_url = "http://localhost:8006"
    
    print("=== PROBANDO ENDPOINTS DE LA API ===\n")
    
    # 1. Listar documentos sin filtro
    print("1. Listando todos los documentos...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents?skip=0&limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Encontrados {data.get('total', 0)} documentos")
            print(f"   [OK] Mostrando {len(data.get('documents', []))} documentos en esta página")
            
            # Mostrar detalles de los primeros 3 documentos
            for i, doc in enumerate(data.get('documents', [])[:3]):
                print(f"   - ID: {doc['id']} | {doc['original_filename']} | Confianza: {doc['confidence_score']}")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 2. Buscar documentos por texto
    print("2. Buscando documentos con 'factura'...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents?skip=0&limit=10&search=factura")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Encontrados {data.get('total', 0)} documentos con 'factura'")
            for doc in data.get('documents', []):
                print(f"   - ID: {doc['id']} | {doc['original_filename']}")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 3. Buscar documentos por texto en contenido
    print("3. Buscando documentos con 'CUIT'...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents?skip=0&limit=10&search=CUIT")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Encontrados {data.get('total', 0)} documentos con 'CUIT'")
            for doc in data.get('documents', []):
                print(f"   - ID: {doc['id']} | {doc['original_filename']}")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 4. Obtener documento específico
    print("4. Obteniendo documento específico (ID: 25)...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/25")
        if response.status_code == 200:
            doc = response.json()
            print(f"   [OK] Documento encontrado: {doc['original_filename']}")
            print(f"   [OK] Texto extraído: {doc['raw_text'][:100]}...")
            print(f"   [OK] Datos extraídos: {len(doc['extracted_data'])} campos")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 5. Probar paginación
    print("5. Probando paginación (página 2)...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents?skip=2&limit=2")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Página 2: {len(data.get('documents', []))} documentos")
            print(f"   [OK] Total: {data.get('total', 0)} documentos")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 6. Probar métodos disponibles
    print("6. Obteniendo métodos disponibles...")
    try:
        response = requests.get(f"{base_url}/api/v1/upload-flexible/methods")
        if response.status_code == 200:
            methods = response.json()
            print(f"   [OK] Métodos OCR: {len(methods.get('ocr_methods', []))}")
            print(f"   [OK] Métodos extracción: {len(methods.get('extraction_methods', []))}")
            print(f"   [OK] Tipos de documento: {len(methods.get('document_types', []))}")
        else:
            print(f"   [ERROR] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")

def test_frontend_responses():
    """Probar que el frontend responda correctamente"""
    
    print("\n=== PROBANDO FRONTEND ===\n")
    
    # 1. Verificar que el frontend esté accesible
    print("1. Verificando acceso al frontend...")
    try:
        response = requests.get("http://localhost:3001")
        if response.status_code == 200:
            print("   [OK] Frontend accesible en http://localhost:3001")
        else:
            print(f"   [ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 2. Verificar que la API esté accesible desde el frontend
    print("2. Verificando conectividad API desde frontend...")
    try:
        # Simular una petición que haría el frontend
        headers = {
            'Origin': 'http://localhost:3001',
            'Referer': 'http://localhost:3001'
        }
        response = requests.get("http://localhost:8006/api/v1/documents?skip=0&limit=5", headers=headers)
        if response.status_code == 200:
            print("   [OK] API accesible desde el frontend")
        else:
            print(f"   [ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_frontend_responses()
    
    print("\n=== RESUMEN ===")
    print("Para probar el frontend manualmente:")
    print("1. Abre http://localhost:3001 en tu navegador")
    print("2. Ve a la sección 'Documentos'")
    print("3. Prueba la búsqueda en la tabla")
    print("4. Prueba la paginación")
    print("5. Haz clic en 'Ver' para ver detalles de un documento")
    print("6. Prueba el botón 'Actualizar'")







