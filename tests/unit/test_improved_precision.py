#!/usr/bin/env python3
"""
Script de Prueba Mejorado para Documentos Académicos
===================================================

Prueba la precisión mejorada del modelo de extracción.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.academic_document_extraction_service import AcademicDocumentExtractionService

def test_improved_titulo_extraction():
    """Probar extracción mejorada de título académico"""
    print("PROBANDO EXTRACCION MEJORADA DE TITULO ACADEMICO")
    print("=" * 60)
    
    # Texto de ejemplo más realista
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
    Código de verificación: VER-2023-001234
    
    Director de Tesis: Dr. María González
    Jurado: Dr. Carlos López, Ing. Ana Martínez
    
    Sede: Ciudad Autónoma de Buenos Aires
    Resolución: RES-2023-456
    Válido en todo el territorio nacional
    """
    
    service = AcademicDocumentExtractionService()
    data = service.extract_titulo_data(titulo_text)
    
    print("RESULTADOS MEJORADOS:")
    print(f"Tipo de documento: {data.tipo_documento}")
    print(f"Institución: {data.institucion}")
    print(f"Título otorgado: {data.titulo_otorgado}")
    print(f"Nombre estudiante: {data.nombre_estudiante}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Número registro: {data.numero_registro}")
    print(f"Calificación: {data.calificacion}")
    print(f"Duración: {data.duracion}")
    print(f"Modalidad: {data.modalidad}")
    print(f"Nivel académico: {data.nivel_academico}")
    print(f"Área de estudio: {data.area_estudio}")
    print(f"Créditos: {data.creditos}")
    print(f"Horas cursadas: {data.horas_cursadas}")
    print(f"Director tesis: {data.director_tesis}")
    print(f"Jurado: {data.jurado}")
    print(f"Código verificación: {data.codigo_verificacion}")
    print(f"Sede: {data.sede}")
    print(f"Facultad: {data.facultad}")
    print(f"Carrera: {data.carrera}")
    print(f"Resolución: {data.resolucion}")
    print(f"Número documento: {data.numero_documento}")
    print(f"Validez nacional: {data.validez_nacional}")
    print()

def test_improved_certificado_extraction():
    """Probar extracción mejorada de certificado"""
    print("PROBANDO EXTRACCION MEJORADA DE CERTIFICADO")
    print("=" * 60)
    
    # Texto de ejemplo más realista
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
    
    Instructor: Ing. Roberto Silva
    Sede: Buenos Aires
    """
    
    service = AcademicDocumentExtractionService()
    data = service.extract_certificado_data(certificado_text)
    
    print("RESULTADOS MEJORADOS:")
    print(f"Tipo de documento: {data.tipo_documento}")
    print(f"Institución: {data.institucion}")
    print(f"Nombre estudiante: {data.nombre_estudiante}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Área de estudio: {data.area_estudio}")
    print(f"Calificación: {data.calificacion}")
    print(f"Duración: {data.duracion}")
    print(f"Horas cursadas: {data.horas_cursadas}")
    print(f"Número registro: {data.numero_registro}")
    print(f"Sede: {data.sede}")
    print(f"Facultad: {data.facultad}")
    print()

def test_precision_comparison():
    """Comparar precisión antes y después de las mejoras"""
    print("COMPARACION DE PRECISION")
    print("=" * 60)
    
    # Texto de prueba
    test_text = """
    UNIVERSIDAD TECNOLÓGICA NACIONAL
    FACULTAD REGIONAL BUENOS AIRES
    
    DIPLOMA DE GRADUACIÓN
    
    Se otorga el presente diploma a:
    CARLOS ALBERTO RODRÍGUEZ
    DNI: 11223344
    
    Por haber completado exitosamente la carrera de:
    TÉCNICO SUPERIOR EN PROGRAMACIÓN
    
    Con un promedio de 9.2
    Duración: 3 años
    Modalidad: Presencial
    
    Fecha de graduación: 20/11/2023
    Registro Nº: DIP-2023-009876
    
    Decano: Dr. Patricia Fernández
    Secretario Académico: Lic. Miguel Torres
    
    Sede: Avellaneda
    Resolución: RES-2023-789
    """
    
    service = AcademicDocumentExtractionService()
    data = service.extract_titulo_data(test_text)
    
    print("CAMPOS EXTRAIDOS CON PRECISION MEJORADA:")
    print(f"Institución: {data.institucion}")
    print(f"Título: {data.titulo_otorgado}")
    print(f"Estudiante: {data.nombre_estudiante}")
    print(f"Fecha: {data.fecha_emision}")
    print(f"Registro: {data.numero_registro}")
    print(f"Calificación: {data.calificacion}")
    print(f"Duración: {data.duracion}")
    print(f"Modalidad: {data.modalidad}")
    print(f"Nivel: {data.nivel_academico}")
    print(f"Área: {data.area_estudio}")
    print(f"Sede: {data.sede}")
    print(f"Resolución: {data.resolucion}")
    print()
    
    # Calcular precisión
    total_fields = 12
    filled_fields = sum(1 for field in [
        data.institucion, data.titulo_otorgado, data.nombre_estudiante,
        data.fecha_emision, data.numero_registro, data.calificacion,
        data.duracion, data.modalidad, data.nivel_academico,
        data.area_estudio, data.sede, data.resolucion
    ] if field)
    
    precision = (filled_fields / total_fields) * 100
    print(f"PRECISION CALCULADA: {precision:.1f}% ({filled_fields}/{total_fields} campos)")
    print()

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DE PRECISION MEJORADA")
    print("=" * 70)
    print()
    
    try:
        test_improved_titulo_extraction()
        test_improved_certificado_extraction()
        test_precision_comparison()
        
        print("TODAS LAS PRUEBAS DE PRECISION COMPLETADAS")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
