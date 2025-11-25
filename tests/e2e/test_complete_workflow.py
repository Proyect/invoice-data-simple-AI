#!/usr/bin/env python3
"""
Test End-to-End (E2E) - Flujo Completo del Sistema
=================================================

Test que simula el flujo completo desde la carga de un documento
hasta la extracción y validación de datos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from app.services.basic_extraction_service import get_basic_extraction_service
from app.services.intelligent_extraction_service import get_intelligent_extraction_service
from app.services.academic_document_extraction_service import get_academic_extraction_service
from app.services.dni_extraction_service import get_dni_extraction_service
from app.services.universal_validation_service import get_universal_validation_service

@pytest.mark.e2e
@pytest.mark.slow
def simulate_document_upload_workflow():
    """Simular flujo completo de carga de documento"""
    print("SIMULANDO FLUJO COMPLETO DE CARGA DE DOCUMENTO")
    print("=" * 60)
    
    # Simular diferentes tipos de documentos
    documents = [
        {
            "name": "factura_ejemplo.pdf",
            "type": "factura",
            "content": """
            FACTURA A
            Nº: 0001-00001234
            Fecha: 15/10/2023
            
            Emisor: EMPRESA EJEMPLO S.A.
            CUIT: 20-12345678-9
            Dirección: AV. CORRIENTES 1234, CABA
            
            Receptor: CLIENTE EJEMPLO
            CUIT: 20-87654321-0
            
            Productos:
            - Producto A: $1000.00
            - Producto B: $500.00
            
            Total: $1500.00
            """
        },
        {
            "name": "titulo_universitario.pdf",
            "type": "titulo",
            "content": """
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
        },
        {
            "name": "dni_tarjeta.pdf",
            "type": "dni",
            "content": """
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
        },
        {
            "name": "certificado_curso.pdf",
            "type": "certificado",
            "content": """
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
        }
    ]
    
    # Obtener servicios
    basic_service = get_basic_extraction_service()
    intelligent_service = get_intelligent_extraction_service()
    academic_service = get_academic_extraction_service()
    dni_service = get_dni_extraction_service()
    validation_service = get_universal_validation_service()
    
    results = []
    
    for i, doc in enumerate(documents, 1):
        print(f"\n{i}. PROCESANDO: {doc['name']}")
        print("-" * 50)
        
        # Paso 1: Detección automática de tipo
        detected_type = basic_service._detect_document_type(doc['content'])
        print(f"Tipo detectado: {detected_type}")
        
        # Paso 2: Extracción de datos
        extracted_data = basic_service.extract_data(doc['content'], detected_type)
        print(f"Campos extraídos: {len([k for k, v in extracted_data.items() if v])}")
        
        # Paso 3: Validación de datos
        try:
            validation_result = validation_service.validate_document(extracted_data)
            validation_score = validation_result.get('confidence', 0)
            print(f"Score de validación: {validation_score:.2f}")
        except Exception as e:
            print(f"Error en validación: {e}")
            validation_score = 0
        
        # Paso 4: Almacenar resultado
        result = {
            'filename': doc['name'],
            'type': detected_type,
            'extracted_fields': len([k for k, v in extracted_data.items() if v]),
            'validation_score': validation_score,
            'data': extracted_data
        }
        results.append(result)
        
        print(f"✓ Documento procesado exitosamente")
    
    return results

def analyze_extraction_quality(results):
    """Analizar calidad de extracción"""
    print("\nANALIZANDO CALIDAD DE EXTRACCION")
    print("=" * 60)
    
    total_documents = len(results)
    total_fields = sum(r['extracted_fields'] for r in results)
    avg_validation_score = sum(r['validation_score'] for r in results) / total_documents
    
    print(f"Total de documentos procesados: {total_documents}")
    print(f"Total de campos extraídos: {total_fields}")
    print(f"Promedio de campos por documento: {total_fields/total_documents:.1f}")
    print(f"Score promedio de validación: {avg_validation_score:.2f}")
    
    # Análisis por tipo de documento
    type_stats = {}
    for result in results:
        doc_type = result['type']
        if doc_type not in type_stats:
            type_stats[doc_type] = {'count': 0, 'fields': 0, 'validation': 0}
        
        type_stats[doc_type]['count'] += 1
        type_stats[doc_type]['fields'] += result['extracted_fields']
        type_stats[doc_type]['validation'] += result['validation_score']
    
    print("\nESTADISTICAS POR TIPO DE DOCUMENTO:")
    print("-" * 40)
    for doc_type, stats in type_stats.items():
        avg_fields = stats['fields'] / stats['count']
        avg_validation = stats['validation'] / stats['count']
        print(f"{doc_type}:")
        print(f"  Documentos: {stats['count']}")
        print(f"  Campos promedio: {avg_fields:.1f}")
        print(f"  Validación promedio: {avg_validation:.2f}")
        print()

def test_error_handling():
    """Probar manejo de errores"""
    print("PROBANDO MANEJO DE ERRORES")
    print("=" * 60)
    
    basic_service = get_basic_extraction_service()
    
    # Casos de error
    error_cases = [
        ("", "Texto vacío"),
        ("Texto sin estructura", "Texto sin estructura"),
        ("123456789", "Solo números"),
        ("!@#$%^&*()", "Solo caracteres especiales"),
        ("a" * 10000, "Texto muy largo")
    ]
    
    for text, description in error_cases:
        try:
            result = basic_service.extract_data(text, "documento")
            print(f"✓ {description}: Procesado sin errores")
        except Exception as e:
            print(f"✗ {description}: Error - {str(e)[:50]}...")
    
    print()

def test_performance_under_load():
    """Probar rendimiento bajo carga"""
    print("PROBANDO RENDIMIENTO BAJO CARGA")
    print("=" * 60)
    
    import time
    
    basic_service = get_basic_extraction_service()
    
    # Texto de prueba
    test_text = """
    FACTURA A
    Nº: 0001-00001234
    Fecha: 15/10/2023
    Emisor: EMPRESA EJEMPLO S.A.
    Receptor: CLIENTE EJEMPLO
    Total: $1500.00
    """
    
    # Probar con diferentes cargas
    loads = [10, 50, 100, 200]
    
    for load in loads:
        start_time = time.time()
        
        for _ in range(load):
            basic_service.extract_data(test_text, "factura")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / load * 1000  # ms
        
        print(f"Carga {load:3d} documentos: {total_time:.3f}s total, {avg_time:.1f}ms promedio")
    
    print()

if __name__ == "__main__":
    print("INICIANDO TESTS END-TO-END (E2E)")
    print("=" * 70)
    print()
    
    try:
        # Ejecutar flujo completo
        results = simulate_document_upload_workflow()
        
        # Analizar resultados
        analyze_extraction_quality(results)
        
        # Probar manejo de errores
        test_error_handling()
        
        # Probar rendimiento
        test_performance_under_load()
        
        print("TODOS LOS TESTS E2E COMPLETADOS EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR EN LOS TESTS E2E: {e}")
        import traceback
        traceback.print_exc()






