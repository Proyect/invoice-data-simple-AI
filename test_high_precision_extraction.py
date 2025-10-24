#!/usr/bin/env python3
"""
Script para probar la extracción de alta precisión con diferentes tipos de facturas
"""

import requests
import json

def test_extraction_precision():
    """Probar la precisión de extracción con diferentes documentos"""
    
    base_url = "http://localhost:8006"
    
    print("=== PROBANDO EXTRACCIÓN DE ALTA PRECISIÓN ===\n")
    
    # 1. Probar con factura AFIP de prueba
    print("1. Probando factura AFIP de prueba...")
    try:
        files = {
            'file': ('factura_afip_test.pdf', open('factura_afip_test.pdf', 'rb'), 'application/pdf')
        }
        data = {'document_type': 'factura'}
        
        response = requests.post(f"{base_url}/api/v1/upload", files=files, data=data)
        files['file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            extracted_data = result['extracted_data']
            
            # Calcular precisión
            precision_score = calculate_precision_score(extracted_data)
            print(f"   [RESULTADO] Precisión: {precision_score:.1f}%")
            print(f"   [RESULTADO] Campos extraídos: {count_extracted_fields(extracted_data)}")
            
            # Mostrar campos más importantes
            show_key_fields(extracted_data)
            
        else:
            print(f"   [ERROR] {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 2. Probar con factura simple anterior
    print("2. Probando factura simple anterior...")
    try:
        files = {
            'file': ('test_invoice.pdf', open('test_invoice.pdf', 'rb'), 'application/pdf')
        }
        data = {'document_type': 'factura'}
        
        response = requests.post(f"{base_url}/api/v1/upload", files=files, data=data)
        files['file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            extracted_data = result['extracted_data']
            
            # Calcular precisión
            precision_score = calculate_precision_score(extracted_data)
            print(f"   [RESULTADO] Precisión: {precision_score:.1f}%")
            print(f"   [RESULTADO] Campos extraídos: {count_extracted_fields(extracted_data)}")
            
            # Mostrar campos más importantes
            show_key_fields(extracted_data)
            
        else:
            print(f"   [ERROR] {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print()
    
    # 3. Mostrar estadísticas generales
    print("3. Estadísticas generales...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents?skip=0&limit=50")
        if response.status_code == 200:
            data = response.json()
            total_docs = data.get('total', 0)
            docs = data.get('documents', [])
            
            # Calcular precisión promedio
            total_precision = 0
            afip_docs = 0
            
            for doc in docs:
                if doc.get('extracted_data', {}).get('tipo_documento') == 'factura_afip':
                    afip_docs += 1
                    precision = calculate_precision_score(doc['extracted_data'])
                    total_precision += precision
            
            if afip_docs > 0:
                avg_precision = total_precision / afip_docs
                print(f"   [ESTADÍSTICAS] Total documentos: {total_docs}")
                print(f"   [ESTADÍSTICAS] Facturas AFIP: {afip_docs}")
                print(f"   [ESTADÍSTICAS] Precisión promedio: {avg_precision:.1f}%")
            else:
                print(f"   [ESTADÍSTICAS] Total documentos: {total_docs}")
                print(f"   [ESTADÍSTICAS] No hay facturas AFIP procesadas")
                
        else:
            print(f"   [ERROR] {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] {e}")

def calculate_precision_score(extracted_data):
    """Calcular puntuación de precisión basada en campos extraídos"""
    
    if not extracted_data:
        return 0.0
    
    # Campos importantes para facturas AFIP
    important_fields = [
        'informacion_comprobante.tipo',
        'informacion_comprobante.punto_venta',
        'informacion_comprobante.numero',
        'informacion_comprobante.fecha_emision',
        'emisor.razon_social',
        'emisor.cuit',
        'emisor.condicion_iva',
        'comprador.razon_social',
        'comprador.cuit',
        'comprador.condicion_iva',
        'totales.total',
        'afip.cae_numero'
    ]
    
    extracted_count = 0
    total_count = len(important_fields)
    
    for field_path in important_fields:
        if get_nested_value(extracted_data, field_path):
            extracted_count += 1
    
    return (extracted_count / total_count) * 100

def get_nested_value(data, path):
    """Obtener valor anidado usando notación de punto"""
    try:
        keys = path.split('.')
        value = data
        for key in keys:
            value = value.get(key, {})
        return value if value and str(value).strip() else None
    except:
        return None

def count_extracted_fields(extracted_data):
    """Contar campos extraídos con datos"""
    if not extracted_data:
        return 0
    
    count = 0
    
    def count_dict(d):
        nonlocal count
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v, dict):
                    count_dict(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            count_dict(item)
                elif v and str(v).strip():
                    count += 1
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, dict):
                    count_dict(item)
                elif item and str(item).strip():
                    count += 1
        elif d and str(d).strip():
            count += 1
    
    count_dict(extracted_data)
    return count

def show_key_fields(extracted_data):
    """Mostrar campos clave extraídos"""
    if not extracted_data:
        return
    
    print("   [CAMPOS CLAVE]")
    
    # Información del comprobante
    comprobante = extracted_data.get('informacion_comprobante', {})
    if comprobante.get('tipo'):
        print(f"     - Tipo: {comprobante['tipo']}")
    if comprobante.get('punto_venta'):
        print(f"     - Punto Venta: {comprobante['punto_venta']}")
    if comprobante.get('numero'):
        print(f"     - Número: {comprobante['numero']}")
    
    # Emisor
    emisor = extracted_data.get('emisor', {})
    if emisor.get('razon_social'):
        print(f"     - Emisor: {emisor['razon_social']}")
    if emisor.get('cuit'):
        print(f"     - CUIT Emisor: {emisor['cuit']}")
    
    # Comprador
    comprador = extracted_data.get('comprador', {})
    if comprador.get('razon_social'):
        print(f"     - Comprador: {comprador['razon_social']}")
    if comprador.get('cuit'):
        print(f"     - CUIT Comprador: {comprador['cuit']}")
    
    # Totales
    totales = extracted_data.get('totales', {})
    if totales.get('total'):
        print(f"     - Total: ${totales['total']}")
    
    # AFIP
    afip = extracted_data.get('afip', {})
    if afip.get('cae_numero'):
        print(f"     - CAE: {afip['cae_numero']}")

if __name__ == "__main__":
    test_extraction_precision()




