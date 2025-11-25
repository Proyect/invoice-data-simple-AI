"""
Datos de Prueba Compartidos
===========================

Datos de prueba reutilizables para diferentes tests.
"""

# Textos de ejemplo para diferentes tipos de documentos
SAMPLE_FACTURA_TEXT = """
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

SAMPLE_TITULO_TEXT = """
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

SAMPLE_DNI_TEXT = """
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

SAMPLE_CERTIFICADO_TEXT = """
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

# Datos extraídos de ejemplo
SAMPLE_EXTRACTED_DATA = {
    "tipo_documento": "factura",
    "numero_factura": "0001-00001234",
    "fecha": "15/10/2023",
    "emisor": "EMPRESA EJEMPLO S.A.",
    "cuit_emisor": "20-12345678-9",
    "receptor": "CLIENTE EJEMPLO",
    "total": 1500.00
}

# Datos de documento de ejemplo
SAMPLE_DOCUMENT_DATA = {
    "filename": "test_document.pdf",
    "original_filename": "test_document.pdf",
    "file_path": "/uploads/test_document.pdf",
    "file_size": 1024,
    "mime_type": "application/pdf",
    "document_type": "factura",
    "status": "uploaded",
    "raw_text": "FACTURA N° 001-2024\nCliente: Test Client\nTotal: $100.00"
}

