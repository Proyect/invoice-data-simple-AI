#!/usr/bin/env python3
"""
Script para probar la extracción mejorada de facturas AFIP
"""

import requests
import json

def test_afip_extraction():
    """Probar extracción de factura AFIP"""
    
    url = "http://localhost:8006/api/v1/upload"
    
    # Preparar archivo
    files = {
        'file': ('factura_afip_test.pdf', open('factura_afip_test.pdf', 'rb'), 'application/pdf')
    }
    
    data = {
        'document_type': 'factura'
    }
    
    try:
        print("Subiendo factura AFIP de prueba...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[OK] Factura AFIP procesada exitosamente!")
            print(f"ID: {result['id']}")
            print(f"Filename: {result['filename']}")
            print(f"Confidence Score: {result['confidence_score']}")
            
            # Mostrar datos extraídos
            extracted_data = result['extracted_data']
            print(f"\n=== DATOS EXTRAÍDOS ===")
            print(f"Tipo de documento: {extracted_data.get('tipo_documento', 'N/A')}")
            
            # Información del comprobante
            comprobante = extracted_data.get('informacion_comprobante', {})
            print(f"\n--- INFORMACIÓN DEL COMPROBANTE ---")
            print(f"Tipo: {comprobante.get('tipo', 'N/A')}")
            print(f"Punto de Venta: {comprobante.get('punto_venta', 'N/A')}")
            print(f"Número: {comprobante.get('numero', 'N/A')}")
            print(f"Fecha Emisión: {comprobante.get('fecha_emision', 'N/A')}")
            print(f"Fecha Vencimiento: {comprobante.get('fecha_vencimiento', 'N/A')}")
            
            # Información del emisor
            emisor = extracted_data.get('emisor', {})
            print(f"\n--- INFORMACIÓN DEL EMISOR ---")
            print(f"Razón Social: {emisor.get('razon_social', 'N/A')}")
            print(f"Domicilio: {emisor.get('domicilio', 'N/A')}")
            print(f"CUIT: {emisor.get('cuit', 'N/A')}")
            print(f"Condición IVA: {emisor.get('condicion_iva', 'N/A')}")
            print(f"Período Desde: {emisor.get('periodo_desde', 'N/A')}")
            print(f"Período Hasta: {emisor.get('periodo_hasta', 'N/A')}")
            
            # Información del comprador
            comprador = extracted_data.get('comprador', {})
            print(f"\n--- INFORMACIÓN DEL COMPRADOR ---")
            print(f"CUIT: {comprador.get('cuit', 'N/A')}")
            print(f"Razón Social: {comprador.get('razon_social', 'N/A')}")
            print(f"Domicilio: {comprador.get('domicilio', 'N/A')}")
            print(f"Condición IVA: {comprador.get('condicion_iva', 'N/A')}")
            print(f"Condición Venta: {comprador.get('condicion_venta', 'N/A')}")
            print(f"Ingresos Brutos: {comprador.get('ingresos_brutos', 'N/A')}")
            print(f"Fecha Inicio Actividades: {comprador.get('fecha_inicio_actividades', 'N/A')}")
            
            # Productos
            productos = extracted_data.get('productos', [])
            print(f"\n--- PRODUCTOS ({len(productos)} items) ---")
            for i, producto in enumerate(productos, 1):
                print(f"Producto {i}:")
                print(f"  Código: {producto.get('codigo', 'N/A')}")
                print(f"  Descripción: {producto.get('descripcion', 'N/A')}")
                print(f"  Cantidad: {producto.get('cantidad', 'N/A')}")
                print(f"  Precio Unitario: {producto.get('precio_unitario', 'N/A')}")
                print(f"  Subtotal: {producto.get('subtotal', 'N/A')}")
            
            # Totales
            totales = extracted_data.get('totales', {})
            print(f"\n--- TOTALES ---")
            print(f"Subtotal: {totales.get('subtotal', 'N/A')}")
            print(f"Otros Tributos: {totales.get('otros_tributos', 'N/A')}")
            print(f"Total: {totales.get('total', 'N/A')}")
            
            # Información AFIP
            afip = extracted_data.get('afip', {})
            print(f"\n--- INFORMACIÓN AFIP ---")
            print(f"CAE Número: {afip.get('cae_numero', 'N/A')}")
            print(f"CAE Vencimiento: {afip.get('cae_vencimiento', 'N/A')}")
            print(f"Página: {afip.get('pagina_actual', 'N/A')}/{afip.get('total_paginas', 'N/A')}")
            
            # Mostrar texto extraído (primeros 200 caracteres)
            raw_text = result['raw_text']
            print(f"\n--- TEXTO EXTRAÍDO (primeros 200 caracteres) ---")
            print(f"{raw_text[:200]}...")
            
        else:
            print(f"[ERROR] Error procesando factura: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        files['file'][1].close()

if __name__ == "__main__":
    test_afip_extraction()










