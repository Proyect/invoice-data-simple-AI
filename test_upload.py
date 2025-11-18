#!/usr/bin/env python3
"""
Test Simplificado de Upload
===========================

Script simple para probar upload de documento.
"""

import requests
import os

def test_upload():
    """Probar upload de documento"""
    url = "http://localhost:8005/upload-optimized"
    
    # Verificar archivo de prueba
    test_file = "test_invoice.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Archivo {test_file} no encontrado")
        print("💡 Crea un archivo PDF de prueba o usa otro archivo")
        return False
    
    print("=== TEST UPLOAD ===")
    
    try:
        # Preparar archivo
        files = {
            'file': (test_file, open(test_file, 'rb'), 'application/pdf')
        }
        data = {'document_type': 'FACTURA'}
        
        print(f"📤 Subiendo {test_file}...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload exitoso")
            print(f"📄 ID: {result.get('document_id', 'N/A')}")
            print(f"📊 Confianza: {result.get('confidence_score', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'files' in locals():
            files['file'][1].close()

if __name__ == "__main__":
    test_upload()





