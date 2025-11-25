"""
Configuración de Tests Optimizada
=================================

Configuración compartida para todos los tests del sistema con fixtures eficientes,
caching, y optimizaciones de rendimiento.
"""

import pytest
import sys
import os
from typing import Generator
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ============================================================================
# Configuración de Base de Datos para Tests
# ============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """Motor de base de datos para tests (sesión única)"""
    # Usar SQLite en memoria para tests rápidos
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Crear todas las tablas
    from src.app.models.base import Base
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Limpiar después de todos los tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Sesión de base de datos con transacciones y rollback automático"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    # Rollback automático para limpiar datos
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_db(db_session: Session) -> Session:
    """Alias para db_session (compatibilidad)"""
    return db_session


# ============================================================================
# Fixtures de Servicios (con scope optimizado)
# ============================================================================

@pytest.fixture(scope="session")
def basic_extraction_service():
    """Fixture para el servicio de extracción básica (sesión única)"""
    from app.services.basic_extraction_service import get_basic_extraction_service
    return get_basic_extraction_service()


@pytest.fixture(scope="session")
def intelligent_extraction_service():
    """Fixture para el servicio de extracción inteligente (sesión única)"""
    from app.services.intelligent_extraction_service import get_intelligent_extraction_service
    return get_intelligent_extraction_service()


@pytest.fixture(scope="session")
def academic_extraction_service():
    """Fixture para el servicio de extracción académica (sesión única)"""
    from app.services.academic_document_extraction_service import get_academic_extraction_service
    return get_academic_extraction_service()


@pytest.fixture(scope="session")
def dni_extraction_service():
    """Fixture para el servicio de extracción de DNI (sesión única)"""
    from app.services.dni_extraction_service import get_dni_extraction_service
    return get_dni_extraction_service()


@pytest.fixture(scope="session")
def validation_service():
    """Fixture para el servicio de validación universal (sesión única)"""
    from app.services.universal_validation_service import get_universal_validation_service
    return get_universal_validation_service()


# ============================================================================
# Fixtures de Datos de Prueba (scope function para aislamiento)
# ============================================================================

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


# ============================================================================
# Fixtures de Modelos y Documentos
# ============================================================================

@pytest.fixture
def sample_document_data():
    """Datos de ejemplo para crear un documento"""
    return {
        "filename": "test_document.pdf",
        "original_filename": "test_document.pdf",
        "file_path": "/uploads/test_document.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "document_type": "factura",
        "status": "uploaded",
        "raw_text": "FACTURA N° 001-2024\nCliente: Test Client\nTotal: $100.00"
    }


@pytest.fixture
def sample_document(db_session: Session, sample_document_data):
    """Documento de prueba persistido en la base de datos"""
    from src.app.models.document_unified import Document
    
    document = Document(**sample_document_data)
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    return document


@pytest.fixture
def sample_extracted_data():
    """Datos extraídos de ejemplo"""
    return {
        "tipo_documento": "factura",
        "numero_factura": "0001-00001234",
        "fecha": "15/10/2023",
        "emisor": "EMPRESA EJEMPLO S.A.",
        "cuit_emisor": "20-12345678-9",
        "receptor": "CLIENTE EJEMPLO",
        "total": 1500.00
    }


# ============================================================================
# Fixtures de API Client
# ============================================================================

@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Cliente de prueba para la API"""
    from src.app.main import app
    
    # Override dependency para usar la sesión de test
    def get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides = {}
    # Si hay una dependencia get_db, reemplazarla
    # app.dependency_overrides[get_db] = get_test_db
    
    return TestClient(app)


# ============================================================================
# Fixtures de Mocks para Servicios Externos
# ============================================================================

@pytest.fixture
def mock_tesseract():
    """Mock de Tesseract OCR"""
    with patch('app.services.ocr_service.tesseract') as mock:
        mock.image_to_string.return_value = "Mocked OCR text"
        mock.image_to_data.return_value = {"text": "Mocked OCR text", "conf": 95}
        yield mock


@pytest.fixture
def mock_spacy():
    """Mock de spaCy NLP"""
    with patch('app.services.basic_extraction_service.nlp') as mock:
        mock_doc = MagicMock()
        mock_doc.ents = []
        mock.return_value = mock_doc
        yield mock


@pytest.fixture
def mock_openai():
    """Mock de OpenAI API"""
    with patch('app.services.intelligent_extraction_service.openai') as mock:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"total": 100.0, "cliente": "Test"}'
        mock.ChatCompletion.create.return_value = mock_response
        yield mock


@pytest.fixture
def mock_redis():
    """Mock de Redis"""
    with patch('app.services.cache_service.redis_client') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        mock.exists.return_value = False
        yield mock


@pytest.fixture
def mock_google_vision():
    """Mock de Google Vision API"""
    with patch('app.services.ocr_service.google_vision_client') as mock:
        mock_response = MagicMock()
        mock_response.text_annotations = [MagicMock(description="Mocked Google Vision text")]
        mock.document_text_detection.return_value = mock_response
        yield mock


@pytest.fixture
def mock_aws_textract():
    """Mock de AWS Textract"""
    with patch('app.services.ocr_service.textract_client') as mock:
        mock_response = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Mocked AWS Textract text'}
            ]
        }
        mock.detect_document_text.return_value = mock_response
        yield mock


# ============================================================================
# Fixtures de Repositories
# ============================================================================

@pytest.fixture
def document_repository(db_session: Session):
    """Repository de documentos para tests"""
    from src.app.repositories.document_repository import DocumentRepository
    return DocumentRepository(db_session)


# ============================================================================
# Fixtures de Archivos
# ============================================================================

@pytest.fixture
def sample_pdf_path(tmp_path):
    """Ruta a un archivo PDF de prueba"""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%Mock PDF content")
    return str(pdf_file)


@pytest.fixture
def sample_pdf_file(tmp_path):
    """Archivo PDF de prueba"""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%Mock PDF content")
    return pdf_file