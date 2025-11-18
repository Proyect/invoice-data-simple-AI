#!/usr/bin/env python3
"""
Test Simplificado de Validación Universal
=========================================

Script simple para probar validación universal.
"""

import requests
import json

def test_validation():
    """Probar validación universal"""
    base_url = "http://localhost:8005"
    
    print("=== TEST VALIDACIÓN UNIVERSAL ===")
    
    # Lista de documentos de prueba
    test_docs = [
        {"file": "recibo_test.pdf", "type": "recibo"},
        {"file": "contrato_test.pdf", "type": "contrato"},
        {"file": "dni_test.pdf", "type": "dni"},
    ]
    
    success = 0
    total = len(test_docs)
    
    for doc in test_docs:
        file_path = doc["file"]
        doc_type = doc["type"]
        
        print(f"\n📄 Probando {file_path} ({doc_type})...")
        
        try:
            # Verificar si existe el archivo
            import os
            if not os.path.exists(file_path):
                print(f"⚠️  Archivo {file_path} no encontrado - saltando")
                continue
            
            # Upload del documento
            url = f"{base_url}/upload-optimized"
            files = {
                'file': (file_path, open(file_path, 'rb'), 'application/pdf')
            }
            data = {'document_type': doc_type}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {doc_type} procesado exitosamente")
                print(f"📊 Confianza: {result.get('confidence_score', 'N/A')}")
                success += 1
            else:
                print(f"❌ Error: {response.status_code}")
            
            files['file'][1].close()
            
        except Exception as e:
            print(f"❌ Error procesando {doc_type}: {e}")
    
    print(f"\n📊 Resultado: {success}/{total} documentos procesados")
    return success > 0

if __name__ == "__main__":
    test_validation()





