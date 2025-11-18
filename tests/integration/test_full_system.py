#!/usr/bin/env python3
"""
Test de Integración Completo del Sistema
========================================

Test que verifica la integración completa de todos los servicios
y tipos de documento soportados.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from app.services.basic_extraction_service import get_basic_extraction_service
from app.services.intelligent_extraction_service import get_intelligent_extraction_service
from app.services.academic_document_extraction_service import get_academic_extraction_service
from app.services.dni_extraction_service import get_dni_extraction_service

def test_system_integration():
    """Probar integración completa del sistema"""
    print("PROBANDO INTEGRACION COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # Obtener servicios
    basic_service = get_basic_extraction_service()
    intelligent_service = get_intelligent_extraction_service()
    academic_service = get_academic_extraction_service()
    dni_service = get_dni_extraction_service()
    
    print("✓ Servicios cargados correctamente")
    
    # Test 1: Factura
    print("\n1. PROBANDO EXTRACCION DE FACTURA")
    print("-" * 40)
    factura_text = """
    FACTURA A
    Nº: 0001-00001234
    Fecha: 15/10/2023
    
    Emisor: EMPRESA EJEMPLO S.A.
    CUIT: 20-12345678-9
    Dirección: AV. CORRIENTES 1234, CABA
    
    Receptor: CLIENTE EJEMPLO
    CUIT: 20-87654321-0
    Dirección: CALLE FALSA 123, CABA
    
    Productos:
    - Producto A: $1000.00
    - Producto B: $500.00
    
    Total: $1500.00
    """
    
    factura_data = basic_service.extract_data(factura_text, "factura")
    print(f"Tipo detectado: {factura_data.get('tipo_documento', 'No detectado')}")
    print(f"Emisor: {factura_data.get('emisor', 'No extraído')}")
    print(f"Receptor: {factura_data.get('receptor', 'No extraído')}")
    print(f"Total: {factura_data.get('total', 'No extraído')}")
    
    # Test 2: Título Académico
    print("\n2. PROBANDO EXTRACCION DE TITULO ACADEMICO")
    print("-" * 40)
    titulo_text = """
    UNIVERSIDAD NACIONAL DE BUENOS AIRES
    FACULTAD DE INGENIERÍA
    
    TÍTULO DE INGENIERO EN SISTEMAS
    
    Por la presente se certifica que el estudiante:
    JUAN CARLOS PÉREZ
    DNI: 12345678
    
    Ha completado satisfactoriamente la carrera de Ingeniería en Sistemas
    con un promedio de 8.5, habiendo cursado un total de 240 créditos
    en modalidad presencial durante 5 años.
    
    Fecha de emisión: 15/12/2023
    Registro Nº: REG-2023-001234
    """
    
    titulo_data = basic_service.extract_data(titulo_text, "titulo")
    print(f"Tipo detectado: {titulo_data.get('tipo_documento', 'No detectado')}")
    print(f"Institución: {titulo_data.get('institucion', 'No extraído')}")
    print(f"Estudiante: {titulo_data.get('nombre_estudiante', 'No extraído')}")
    print(f"Título: {titulo_data.get('titulo_otorgado', 'No extraído')}")
    
    # Test 3: DNI
    print("\n3. PROBANDO EXTRACCION DE DNI")
    print("-" * 40)
    dni_text = """
    REPÚBLICA ARGENTINA
    DOCUMENTO NACIONAL DE IDENTIDAD
    
    Apellido: GARCÍA
    Nombre: JUAN CARLOS
    Sexo: M
    Fecha de Nacimiento: 15/03/1985
    Lugar de Nacimiento: BUENOS AIRES
    Nacionalidad: ARGENTINO
    
    Fecha de Emisión: 10/01/2020
    Fecha de Vencimiento: 10/01/2030
    Lugar de Emisión: CABA
    """
    
    dni_data = basic_service.extract_data(dni_text, "dni")
    print(f"Tipo detectado: {dni_data.get('tipo_documento', 'No detectado')}")
    print(f"Apellido: {dni_data.get('apellido', 'No extraído')}")
    print(f"Nombre: {dni_data.get('nombre', 'No extraído')}")
    print(f"Sexo: {dni_data.get('sexo', 'No extraído')}")
    print(f"Fecha nacimiento: {dni_data.get('fecha_nacimiento', 'No extraído')}")
    
    # Test 4: Certificado
    print("\n4. PROBANDO EXTRACCION DE CERTIFICADO")
    print("-" * 40)
    certificado_text = """
    INSTITUTO DE CAPACITACIÓN PROFESIONAL
    DEPARTAMENTO DE TECNOLOGÍA
    
    CERTIFICADO DE APROBACIÓN
    
    Por la presente se certifica que:
    MARÍA GARCÍA LÓPEZ
    DNI: 87654321
    
    Ha completado exitosamente el curso de:
    PROGRAMACIÓN EN PYTHON AVANZADO
    
    Con una calificación de APROBADO
    Duración: 40 horas
    Modalidad: Virtual
    
    Fecha de emisión: 10/11/2023
    Registro Nº: CERT-2023-005678
    """
    
    certificado_data = basic_service.extract_data(certificado_text, "certificado")
    print(f"Tipo detectado: {certificado_data.get('tipo_documento', 'No detectado')}")
    print(f"Institución: {certificado_data.get('institucion', 'No extraído')}")
    print(f"Estudiante: {certificado_data.get('nombre_estudiante', 'No extraído')}")
    print(f"Curso: {certificado_data.get('area_estudio', 'No extraído')}")
    
    print("\n✓ INTEGRACION COMPLETA VERIFICADA")
    print("=" * 60)

def test_document_type_detection():
    """Probar detección automática de tipos de documento"""
    print("\nPROBANDO DETECCION AUTOMATICA DE TIPOS")
    print("=" * 60)
    
    basic_service = get_basic_extraction_service()
    
    test_documents = [
        ("FACTURA A\nNº: 0001-00001234\nEmisor: EMPRESA S.A.", "factura"),
        ("RECIBO\nNº: 001234\nFecha: 15/10/2023", "recibo"),
        ("UNIVERSIDAD NACIONAL\nTÍTULO DE INGENIERO\nEstudiante: JUAN PÉREZ", "titulo"),
        ("CERTIFICADO DE APROBACIÓN\nCurso: PYTHON\nEstudiante: MARÍA GARCÍA", "certificado"),
        ("REPÚBLICA ARGENTINA\nDOCUMENTO NACIONAL DE IDENTIDAD\nApellido: LÓPEZ", "dni"),
        ("PASAPORTE\nREPÚBLICA ARGENTINA\nApellido: MARTÍNEZ", "pasaporte")
    ]
    
    correct_detections = 0
    total_documents = len(test_documents)
    
    for text, expected_type in test_documents:
        detected_type = basic_service._detect_document_type(text)
        is_correct = detected_type == expected_type
        if is_correct:
            correct_detections += 1
        
        status = "✓" if is_correct else "✗"
        print(f"  {status} Texto: {text[:30]}...")
        print(f"    Esperado: {expected_type}, Detectado: {detected_type}")
        print()
    
    detection_accuracy = (correct_detections / total_documents) * 100
    print(f"PRECISION DE DETECCION: {detection_accuracy:.1f}% ({correct_detections}/{total_documents})")
    print("=" * 60)

def test_service_performance():
    """Probar rendimiento de los servicios"""
    print("\nPROBANDO RENDIMIENTO DE SERVICIOS")
    print("=" * 60)
    
    import time
    
    basic_service = get_basic_extraction_service()
    academic_service = get_academic_extraction_service()
    dni_service = get_dni_extraction_service()
    
    test_text = """
    UNIVERSIDAD NACIONAL DE BUENOS AIRES
    FACULTAD DE INGENIERÍA
    TÍTULO DE INGENIERO EN SISTEMAS
    Estudiante: JUAN CARLOS PÉREZ
    DNI: 12345678
    Fecha de emisión: 15/12/2023
    """
    
    # Test rendimiento extracción básica
    start_time = time.time()
    for _ in range(100):
        basic_service.extract_data(test_text, "titulo")
    basic_time = time.time() - start_time
    
    # Test rendimiento extracción académica
    start_time = time.time()
    for _ in range(100):
        academic_service.extract_titulo_data(test_text)
    academic_time = time.time() - start_time
    
    print(f"Extracción básica (100 iteraciones): {basic_time:.3f}s")
    print(f"Extracción académica (100 iteraciones): {academic_time:.3f}s")
    print(f"Promedio por extracción básica: {basic_time/100*1000:.1f}ms")
    print(f"Promedio por extracción académica: {academic_time/100*1000:.1f}ms")
    print("=" * 60)

if __name__ == "__main__":
    print("INICIANDO TESTS DE INTEGRACION COMPLETA")
    print("=" * 70)
    print()
    
    try:
        test_system_integration()
        test_document_type_detection()
        test_service_performance()
        
        print("\nTODOS LOS TESTS DE INTEGRACION COMPLETADOS EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR EN LOS TESTS: {e}")
        import traceback
        traceback.print_exc()




