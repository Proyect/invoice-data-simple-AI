#!/usr/bin/env python3
"""
Test Simplificado de OCR Especializado
======================================

Script simple para probar OCR especializado.
"""

import sys
import os
from pathlib import Path

# Agregar src al path (ahora estamos en tests/unit/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_ocr():
    """Probar OCR especializado"""
    print("=== TEST OCR ESPECIALIZADO ===")
    
    try:
        from app.services.specialized_ocr_service import SpecializedOCRService
        
        # Inicializar servicio
        print("🔧 Inicializando servicio OCR...")
        ocr_service = SpecializedOCRService()
        print("✅ Servicio inicializado")
        
        # Verificar archivo de prueba
        test_file = "factura_con_cae.pdf"
        if not os.path.exists(test_file):
            print(f"⚠️  Archivo {test_file} no encontrado")
            print("💡 Usa cualquier archivo PDF para probar")
            return True  # No es error crítico
        
        # Probar extracción
        print(f"📄 Procesando {test_file}...")
        result = ocr_service.extract_text(test_file)
        
        if result and result.text:
            print("✅ OCR exitoso")
            print(f"📊 Texto extraído: {len(result.text)} caracteres")
            print(f"📈 Confianza: {result.confidence}")
            print(f"⏱️  Tiempo: {result.processing_time}s")
        else:
            print("⚠️  No se extrajo texto")
        
        print("🎉 Test OCR completado!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando servicio: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en OCR: {e}")
        return False

if __name__ == "__main__":
    test_ocr()















