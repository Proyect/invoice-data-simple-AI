"""
Configuración de Tests
=====================

Configuración compartida para todos los tests del sistema.
"""

import pytest
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def basic_extraction_service():
    """Fixture para el servicio de extracción básica"""
    from app.services.basic_extraction_service import get_basic_extraction_service
    return get_basic_extraction_service()

@pytest.fixture
def intelligent_extraction_service():
    """Fixture para el servicio de extracción inteligente"""
    from app.services.intelligent_extraction_service import get_intelligent_extraction_service
    return get_intelligent_extraction_service()

@pytest.fixture
def academic_extraction_service():
    """Fixture para el servicio de extracción académica"""
    from app.services.academic_document_extraction_service import get_academic_extraction_service
    return get_academic_extraction_service()

@pytest.fixture
def dni_extraction_service():
    """Fixture para el servicio de extracción de DNI"""
    from app.services.dni_extraction_service import get_dni_extraction_service
    return get_dni_extraction_service()

@pytest.fixture
def validation_service():
    """Fixture para el servicio de validación universal"""
    from app.services.universal_validation_service import get_universal_validation_service
    return get_universal_validation_service()

@pytest.fixture
def sample_factura_text():
    """Texto de ejemplo de factura"""
    return """
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

@pytest.fixture
def sample_titulo_text():
    """Texto de ejemplo de título académico"""
    return """
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

@pytest.fixture
def sample_dni_text():
    """Texto de ejemplo de DNI"""
    return """
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

@pytest.fixture
def sample_certificado_text():
    """Texto de ejemplo de certificado"""
    return """
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