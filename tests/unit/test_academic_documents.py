#!/usr/bin/env python3
"""
Script de Prueba para Documentos Académicos
==========================================

Prueba la extracción de datos de títulos y certificados.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.academic_document_extraction_service import AcademicDocumentExtractionService

@pytest.mark.unit
def test_titulo_extraction():
    """Probar extracción de título académico"""
    print("PROBANDO EXTRACCION DE TITULO ACADEMICO")
    print("=" * 50)
    
    # Texto de ejemplo de un título universitario
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

def test_certificado_extraction():
    """Probar extracción de certificado"""
    print("PROBANDO EXTRACCION DE CERTIFICADO")
    print("=" * 50)
    
    # Texto de ejemplo de un certificado de curso
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

def test_diploma_extraction():
    """Probar extracción de diploma"""
    print("PROBANDO EXTRACCION DE DIPLOMA")
    print("=" * 50)
    
    # Texto de ejemplo de un diploma
    diploma_text = """
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
    data = service.extract_titulo_data(diploma_text)  # Los diplomas usan el mismo método que títulos
    
    print(f"Tipo de documento: {data.tipo_documento}")
    print(f"Institución: {data.institucion}")
    print(f"Título otorgado: {data.titulo_otorgado}")
    print(f"Nombre estudiante: {data.nombre_estudiante}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Calificación: {data.calificacion}")
    print(f"Duración: {data.duracion}")
    print(f"Modalidad: {data.modalidad}")
    print(f"Nivel académico: {data.nivel_academico}")
    print(f"Área de estudio: {data.area_estudio}")
    print(f"Sede: {data.sede}")
    print(f"Facultad: {data.facultad}")
    print(f"Carrera: {data.carrera}")
    print()

def test_licencia_extraction():
    """Probar extracción de licencia"""
    print("PROBANDO EXTRACCION DE LICENCIA")
    print("=" * 50)
    
    # Texto de ejemplo de una licencia profesional
    licencia_text = """
    COLEGIO DE INGENIEROS DE LA PROVINCIA DE BUENOS AIRES
    
    LICENCIA PROFESIONAL
    
    Se otorga la presente licencia a:
    ANA LUCÍA MARTÍNEZ
    DNI: 55667788
    
    Para ejercer la profesión de:
    INGENIERA EN SISTEMAS
    
    Número de matrícula: MAT-2023-123456
    Fecha de emisión: 05/12/2023
    Válida hasta: 05/12/2026
    
    Código de verificación: LIC-2023-123456
    Sede: La Plata
    """
    
    service = AcademicDocumentExtractionService()
    data = service.extract_titulo_data(licencia_text)
    
    print(f"Tipo de documento: {data.tipo_documento}")
    print(f"Institución: {data.institucion}")
    print(f"Título otorgado: {data.titulo_otorgado}")
    print(f"Nombre estudiante: {data.nombre_estudiante}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Fecha vencimiento: {data.fecha_vencimiento}")
    print(f"Número registro: {data.numero_registro}")
    print(f"Código verificación: {data.codigo_verificacion}")
    print(f"Sede: {data.sede}")
    print()

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DE DOCUMENTOS ACADEMICOS")
    print("=" * 60)
    print()
    
    try:
        test_titulo_extraction()
        test_certificado_extraction()
        test_diploma_extraction()
        test_licencia_extraction()
        
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
