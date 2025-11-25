#!/usr/bin/env python3
"""
Test Simplificado de Factura Realista
====================================

Script simple para probar extracción de factura AFIP.
"""

import requests
import json
import os

def test_invoice():
    """Probar factura AFIP"""
    url = "http://localhost:8005/upload-optimized"
    
    # Verificar que existe el archivo
    if not os.path.exists("factura_afip_realista.pdf"):
        print("❌ Archivo factura_afip_realista.pdf no encontrado")
        return False
    
    print("=== TEST FACTURA AFIP ===")
    
    try:
        # Preparar archivo
        files = {
            'file': ('factura_afip_realista.pdf', open('factura_afip_realista.pdf', 'rb'), 'application/pdf')
        }
        data = {'document_type': 'FACTURA'}
        
        print("📤 Subiendo factura...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Factura procesada exitosamente")
            print(f"📄 ID: {result.get('document_id', 'N/A')}")
            print(f"📊 Confianza: {result.get('confidence_score', 'N/A')}")
            
            # Mostrar datos extraídos
            if 'extracted_data' in result:
                data = result['extracted_data']
                print("📋 Datos extraídos:")
                for key, value in data.items():
                    if value:
                        print(f"   {key}: {value}")
            
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
    test_invoice()








