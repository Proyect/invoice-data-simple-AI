#!/usr/bin/env python3
"""
Script para probar la validación completa de CAE
"""

import requests
import json

def test_cae_validation():
    """Probar validación de CAE con factura realista"""
    
    url = "http://localhost:8006/api/v1/upload"
    
    # Preparar archivo
    files = {
        'file': ('factura_con_cae.pdf', open('factura_con_cae.pdf', 'rb'), 'application/pdf')
    }
    
    data = {
        'document_type': 'factura'
    }
    
    try:
        print("=== PROBANDO VALIDACIÓN COMPLETA DE CAE ===")
        print("Subiendo factura con CAE realista...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[OK] Factura con CAE procesada exitosamente!")
            print(f"ID: {result['id']}")
            print(f"Filename: {result['filename']}")
            print(f"Confidence Score: {result['confidence_score']}")
            
            # Mostrar datos extraídos
            extracted_data = result['extracted_data']
            
            # Mostrar CAE extraído
            afip_info = extracted_data.get('afip', {})
            cae_numero = afip_info.get('cae_numero', '')
            cae_vencimiento = afip_info.get('cae_vencimiento', '')
            
            print(f"\n=== CAE EXTRAÍDO ===")
            print(f"CAE Número: {cae_numero}")
            print(f"CAE Vencimiento: {cae_vencimiento}")
            
            # Mostrar validación AFIP
            validacion_afip = extracted_data.get('validacion_afip', {})
            
            print(f"\n=== VALIDACIÓN AFIP ===")
            print(f"Factura Válida: {validacion_afip.get('is_valid', False)}")
            
            if validacion_afip.get('errors'):
                print(f"Errores: {validacion_afip['errors']}")
            
            if validacion_afip.get('warnings'):
                print(f"Advertencias: {validacion_afip['warnings']}")
            
            # Mostrar campos validados
            validated_fields = validacion_afip.get('validated_fields', {})
            print(f"\n=== CAMPOS VALIDADOS ===")
            
            for field, validation in validated_fields.items():
                status = "✓" if validation.get('valid', False) else "✗"
                print(f"{status} {field}: {validation.get('error', 'Válido')}")
            
            # Mostrar información del comprobante
            comprobante = extracted_data.get('informacion_comprobante', {})
            print(f"\n=== INFORMACIÓN DEL COMPROBANTE ===")
            print(f"Tipo: {comprobante.get('tipo', 'N/A')}")
            print(f"Punto de Venta: {comprobante.get('punto_venta', 'N/A')}")
            print(f"Número: {comprobante.get('numero', 'N/A')}")
            print(f"Fecha Emisión: {comprobante.get('fecha_emision', 'N/A')}")
            
            # Mostrar emisor
            emisor = extracted_data.get('emisor', {})
            print(f"\n=== EMISOR ===")
            print(f"Razón Social: {emisor.get('razon_social', 'N/A')}")
            print(f"CUIT: {emisor.get('cuit', 'N/A')}")
            print(f"Condición IVA: {emisor.get('condicion_iva', 'N/A')}")
            
            # Mostrar comprador
            comprador = extracted_data.get('comprador', {})
            print(f"\n=== COMPRADOR ===")
            print(f"Razón Social: {comprador.get('razon_social', 'N/A')}")
            print(f"CUIT: {comprador.get('cuit', 'N/A')}")
            print(f"Condición IVA: {comprador.get('condicion_iva', 'N/A')}")
            
            # Mostrar totales
            totales = extracted_data.get('totales', {})
            print(f"\n=== TOTALES ===")
            print(f"Subtotal: {totales.get('subtotal', 'N/A')}")
            print(f"Total: {totales.get('total', 'N/A')}")
            
            # Análisis de precisión
            print(f"\n=== ANÁLISIS DE PRECISIÓN ===")
            precision_analysis = analyze_precision_with_validation(extracted_data)
            for section, score in precision_analysis.items():
                print(f"{section}: {score:.1f}%")
            
        else:
            print(f"[ERROR] Error procesando factura: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        files['file'][1].close()

def analyze_precision_with_validation(extracted_data):
    """Analizar precisión incluyendo validación"""
    
    scores = {}
    
    # Información del comprobante
    comprobante = extracted_data.get('informacion_comprobante', {})
    comprobante_fields = ['tipo', 'punto_venta', 'numero', 'fecha_emision']
    comprobante_score = sum(1 for field in comprobante_fields if comprobante.get(field, '').strip())
    scores['Comprobante'] = (comprobante_score / len(comprobante_fields)) * 100
    
    # Información del emisor
    emisor = extracted_data.get('emisor', {})
    emisor_fields = ['razon_social', 'cuit', 'condicion_iva']
    emisor_score = sum(1 for field in emisor_fields if emisor.get(field, '').strip())
    scores['Emisor'] = (emisor_score / len(emisor_fields)) * 100
    
    # Información del comprador
    comprador = extracted_data.get('comprador', {})
    comprador_fields = ['cuit', 'razon_social', 'condicion_iva', 'condicion_venta']
    comprador_score = sum(1 for field in comprador_fields if comprador.get(field, '').strip())
    scores['Comprador'] = (comprador_score / len(comprador_fields)) * 100
    
    # Totales
    totales = extracted_data.get('totales', {})
    totales_fields = ['subtotal', 'total']
    totales_score = sum(1 for field in totales_fields if totales.get(field, '').strip())
    scores['Totales'] = (totales_score / len(totales_fields)) * 100
    
    # Información AFIP
    afip = extracted_data.get('afip', {})
    afip_fields = ['cae_numero', 'cae_vencimiento']
    afip_score = sum(1 for field in afip_fields if afip.get(field, '').strip())
    scores['AFIP'] = (afip_score / len(afip_fields)) * 100
    
    # Validación
    validacion = extracted_data.get('validacion_afip', {})
    if validacion:
        validated_fields = validacion.get('validated_fields', {})
        total_validations = len(validated_fields)
        valid_validations = sum(1 for v in validated_fields.values() if v.get('valid', False))
        scores['Validación'] = (valid_validations / total_validations * 100) if total_validations > 0 else 0
    else:
        scores['Validación'] = 0
    
    return scores

if __name__ == "__main__":
    test_cae_validation()







