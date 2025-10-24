#!/usr/bin/env python3
"""
Tests Unitarios para Extracción de DNI Argentinos
================================================

Tests específicos para el servicio de extracción de DNI argentinos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from app.services.dni_extraction_service import DNIExtractionService, DNIData

def test_dni_tarjeta_extraction():
    """Probar extracción de DNI tarjeta"""
    print("PROBANDO EXTRACCION DE DNI TARJETA")
    print("=" * 50)
    
    # Texto de ejemplo de DNI tarjeta
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
    Nº de Trámite: 12345678
    Código de Verificación: ABC123
    
    Domicilio: AV. CORRIENTES 1234, CABA
    Estado Civil: SOLTERO
    Profesión: INGENIERO
    """
    
    service = DNIExtractionService()
    data = service.extract_dni_data(dni_text)
    
    print("RESULTADOS DNI TARJETA:")
    print(f"Tipo documento: {data.tipo_documento}")
    print(f"Número DNI: {data.numero_dni}")
    print(f"Apellido: {data.apellido}")
    print(f"Nombre: {data.nombre}")
    print(f"Sexo: {data.sexo}")
    print(f"Fecha nacimiento: {data.fecha_nacimiento}")
    print(f"Lugar nacimiento: {data.lugar_nacimiento}")
    print(f"Nacionalidad: {data.nacionalidad}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Fecha vencimiento: {data.fecha_vencimiento}")
    print(f"Lugar emisión: {data.lugar_emision}")
    print(f"Número trámite: {data.numero_tramite}")
    print(f"Código verificación: {data.codigo_verificacion}")
    print(f"Domicilio: {data.domicilio}")
    print(f"Estado civil: {data.estado_civil}")
    print(f"Profesión: {data.profesion}")
    print()

def test_dni_libreta_extraction():
    """Probar extracción de libreta cívica"""
    print("PROBANDO EXTRACCION DE LIBRETA CIVICA")
    print("=" * 50)
    
    # Texto de ejemplo de libreta cívica
    libreta_text = """
    LIBRETA CÍVICA
    Nº: 12345678
    
    Apellido: MARTÍNEZ
    Nombre: MARÍA ELENA
    Sexo: F
    Fecha de Nacimiento: 22/07/1990
    Lugar de Nacimiento: CÓRDOBA
    Nacionalidad: ARGENTINA
    
    Fecha de Emisión: 05/06/2018
    Lugar de Emisión: CÓRDOBA
    """
    
    service = DNIExtractionService()
    data = service.extract_dni_data(libreta_text)
    
    print("RESULTADOS LIBRETA CIVICA:")
    print(f"Tipo documento: {data.tipo_documento}")
    print(f"Número DNI: {data.numero_dni}")
    print(f"Apellido: {data.apellido}")
    print(f"Nombre: {data.nombre}")
    print(f"Sexo: {data.sexo}")
    print(f"Fecha nacimiento: {data.fecha_nacimiento}")
    print(f"Lugar nacimiento: {data.lugar_nacimiento}")
    print(f"Nacionalidad: {data.nacionalidad}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Lugar emisión: {data.lugar_emision}")
    print()

def test_pasaporte_extraction():
    """Probar extracción de pasaporte argentino"""
    print("PROBANDO EXTRACCION DE PASAPORTE")
    print("=" * 50)
    
    # Texto de ejemplo de pasaporte
    pasaporte_text = """
    REPÚBLICA ARGENTINA
    PASAPORTE
    
    Apellido: LÓPEZ
    Nombre: CARLOS ALBERTO
    Sexo: M
    Fecha de Nacimiento: 10/12/1988
    Lugar de Nacimiento: ROSARIO
    Nacionalidad: ARGENTINO
    
    Fecha de Emisión: 15/03/2022
    Fecha de Vencimiento: 15/03/2032
    Lugar de Emisión: ROSARIO
    Nº de Trámite: 87654321
    """
    
    service = DNIExtractionService()
    data = service.extract_dni_data(pasaporte_text)
    
    print("RESULTADOS PASAPORTE:")
    print(f"Tipo documento: {data.tipo_documento}")
    print(f"Número DNI: {data.numero_dni}")
    print(f"Apellido: {data.apellido}")
    print(f"Nombre: {data.nombre}")
    print(f"Sexo: {data.sexo}")
    print(f"Fecha nacimiento: {data.fecha_nacimiento}")
    print(f"Lugar nacimiento: {data.lugar_nacimiento}")
    print(f"Nacionalidad: {data.nacionalidad}")
    print(f"Fecha emisión: {data.fecha_emision}")
    print(f"Fecha vencimiento: {data.fecha_vencimiento}")
    print(f"Lugar emisión: {data.lugar_emision}")
    print(f"Número trámite: {data.numero_tramite}")
    print()

def test_dni_validation():
    """Probar validación de números de DNI"""
    print("PROBANDO VALIDACION DE DNI")
    print("=" * 50)
    
    service = DNIExtractionService()
    
    # DNI válidos
    valid_dnis = ["12345678", "8765432", "1234567", "99999999"]
    # DNI inválidos
    invalid_dnis = ["123456", "123456789", "abc12345", "1234567a", ""]
    
    print("DNI VALIDOS:")
    for dni in valid_dnis:
        is_valid = service.validate_dni_number(dni)
        print(f"  {dni}: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    
    print("\nDNI INVALIDOS:")
    for dni in invalid_dnis:
        is_valid = service.validate_dni_number(dni)
        print(f"  {dni}: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    print()

def test_precision_calculation():
    """Calcular precisión de extracción de DNI"""
    print("CALCULANDO PRECISION DE EXTRACCION DNI")
    print("=" * 50)
    
    # Texto de prueba completo
    test_text = """
    REPÚBLICA ARGENTINA
    DOCUMENTO NACIONAL DE IDENTIDAD
    
    Apellido: RODRÍGUEZ
    Nombre: ANA MARÍA
    Sexo: F
    Fecha de Nacimiento: 08/11/1992
    Lugar de Nacimiento: MENDOZA
    Nacionalidad: ARGENTINA
    
    Fecha de Emisión: 20/09/2021
    Fecha de Vencimiento: 20/09/2031
    Lugar de Emisión: MENDOZA
    Nº de Trámite: 11223344
    Código de Verificación: XYZ789
    
    Domicilio: CALLE SAN MARTÍN 567, MENDOZA
    Estado Civil: CASADA
    Profesión: MÉDICA
    """
    
    service = DNIExtractionService()
    data = service.extract_dni_data(test_text)
    
    # Campos esperados
    expected_fields = [
        ("tipo_documento", "dni_tarjeta"),
        ("apellido", "RODRÍGUEZ"),
        ("nombre", "ANA MARÍA"),
        ("sexo", "F"),
        ("fecha_nacimiento", "08/11/1992"),
        ("lugar_nacimiento", "MENDOZA"),
        ("nacionalidad", "ARGENTINA"),
        ("fecha_emision", "20/09/2021"),
        ("fecha_vencimiento", "20/09/2031"),
        ("lugar_emision", "MENDOZA"),
        ("numero_tramite", "11223344"),
        ("codigo_verificacion", "XYZ789"),
        ("domicilio", "CALLE SAN MARTÍN 567, MENDOZA"),
        ("estado_civil", "CASADA"),
        ("profesion", "MÉDICA")
    ]
    
    correct_fields = 0
    total_fields = len(expected_fields)
    
    print("CAMPOS EXTRAIDOS:")
    for field_name, expected_value in expected_fields:
        actual_value = getattr(data, field_name)
        is_correct = actual_value == expected_value
        if is_correct:
            correct_fields += 1
        
        status = "OK" if is_correct else "FAIL"
        print(f"  {status} {field_name}: {actual_value} (esperado: {expected_value})")
    
    precision = (correct_fields / total_fields) * 100
    print(f"\nPRECISION: {precision:.1f}% ({correct_fields}/{total_fields} campos)")
    print()

if __name__ == "__main__":
    print("INICIANDO TESTS DE EXTRACCION DNI")
    print("=" * 60)
    print()
    
    try:
        test_dni_tarjeta_extraction()
        test_dni_libreta_extraction()
        test_pasaporte_extraction()
        test_dni_validation()
        test_precision_calculation()
        
        print("TODOS LOS TESTS DE DNI COMPLETADOS")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR EN LOS TESTS: {e}")
        import traceback
        traceback.print_exc()
