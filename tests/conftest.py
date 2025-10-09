"""
Configuración y fixtures compartidos para tests
"""
import pytest
import sys
import os
from pathlib import Path
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Crea una base de datos de prueba en memoria para cada test
    """
    # Crear engine de SQLite en memoria
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de prueba
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Cliente de prueba de FastAPI con base de datos de test
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# FILE FIXTURES
# ============================================================================

@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """
    Crea un PDF de prueba simple
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = tmp_path / "test_invoice.pdf"
    
    # Crear PDF simple
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "FACTURA")
    c.drawString(100, 730, "Número: 0001-00000001")
    c.drawString(100, 710, "Fecha: 15/10/2024")
    c.drawString(100, 690, "Emisor: Test Company SA")
    c.drawString(100, 670, "CUIT: 20-12345678-9")
    c.drawString(100, 650, "Cliente: Test Cliente")
    c.drawString(100, 630, "Total: $1,234.56")
    c.save()
    
    return pdf_path


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """
    Crea una imagen de prueba simple
    """
    from PIL import Image, ImageDraw, ImageFont
    
    img_path = tmp_path / "test_invoice.jpg"
    
    # Crear imagen simple
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Agregar texto
    text_lines = [
        "FACTURA",
        "Número: 0001-00000001",
        "Fecha: 15/10/2024",
        "Emisor: Test Company SA",
        "CUIT: 20-12345678-9",
        "Cliente: Test Cliente",
        "Total: $1,234.56"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill='black')
        y_position += 40
    
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_upload_file(sample_pdf_path: Path):
    """
    Crea un UploadFile simulado para tests
    """
    from io import BytesIO
    from fastapi import UploadFile
    
    with open(sample_pdf_path, 'rb') as f:
        content = f.read()
    
    file = UploadFile(
        filename="test_invoice.pdf",
        file=BytesIO(content),
        content_type="application/pdf"
    )
    
    return file


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_tesseract(monkeypatch):
    """
    Mock de pytesseract para tests sin OCR real
    """
    def mock_image_to_string(image, **kwargs):
        return """
        FACTURA
        Número: 0001-00000001
        Fecha: 15/10/2024
        Emisor: Test Company SA
        CUIT: 20-12345678-9
        Cliente: Test Cliente
        Subtotal: $1,000.00
        IVA (21%): $210.00
        Total: $1,234.56
        """
    
    def mock_image_to_data(image, **kwargs):
        return {
            'text': ['FACTURA', 'Número:', '0001-00000001'],
            'conf': [95, 90, 85]
        }
    
    def mock_get_tesseract_version():
        return "5.0.0"
    
    import pytesseract
    monkeypatch.setattr(pytesseract, "image_to_string", mock_image_to_string)
    monkeypatch.setattr(pytesseract, "image_to_data", mock_image_to_data)
    monkeypatch.setattr(pytesseract, "get_tesseract_version", mock_get_tesseract_version)


@pytest.fixture
def mock_spacy(monkeypatch):
    """
    Mock de spaCy para tests sin modelo NLP real
    """
    class MockEntity:
        def __init__(self, text, label):
            self.text = text
            self.label_ = label
    
    class MockDoc:
        def __init__(self, text):
            self.text = text
            self.ents = [
                MockEntity("Test Company SA", "ORG"),
                MockEntity("Test Cliente", "PER"),
                MockEntity("15/10/2024", "DATE"),
            ]
    
    class MockNLP:
        def __call__(self, text):
            return MockDoc(text)
    
    import spacy
    monkeypatch.setattr(spacy, "load", lambda x: MockNLP())


@pytest.fixture
def mock_openai(monkeypatch):
    """
    Mock de OpenAI API para tests sin llamadas reales
    """
    class MockMessage:
        def __init__(self):
            self.content = """{
                "numero_factura": "0001-00000001",
                "fecha": "15/10/2024",
                "emisor": {
                    "nombre": "Test Company SA",
                    "cuit": "20-12345678-9"
                },
                "receptor": {
                    "nombre": "Test Cliente"
                },
                "totales": {
                    "subtotal": "1000.00",
                    "iva": "210.00",
                    "total": "1234.56"
                }
            }"""
    
    class MockChoice:
        def __init__(self):
            self.message = MockMessage()
    
    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
    
    class MockCompletions:
        async def create(self, **kwargs):
            return MockResponse()
    
    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()
    
    class MockOpenAI:
        def __init__(self, **kwargs):
            self.chat = MockChat()
    
    import openai
    monkeypatch.setattr(openai, "OpenAI", MockOpenAI)


@pytest.fixture
def mock_redis(monkeypatch):
    """
    Mock de Redis para tests sin servidor Redis
    """
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value):
            self.data[key] = value
            return True
        
        def setex(self, key, ttl, value):
            self.data[key] = value
            return True
        
        def delete(self, *keys):
            for key in keys:
                if key in self.data:
                    del self.data[key]
            return len(keys)
        
        def keys(self, pattern):
            # Implementación simple de pattern matching
            import fnmatch
            return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]
        
        def ping(self):
            return True
    
    import redis
    monkeypatch.setattr(redis, "Redis", lambda **kwargs: MockRedis())


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_extracted_data():
    """
    Datos extraídos de ejemplo
    """
    return {
        "tipo_documento": "factura",
        "numero_factura": "0001-00000001",
        "fecha": "15/10/2024",
        "emisor": "Test Company SA",
        "receptor": "Test Cliente",
        "cuit": "20-12345678-9",
        "totales": {
            "subtotal": "1000.00",
            "iva": "210.00",
            "total": "1234.56"
        },
        "items": [
            {
                "descripcion": "Producto de prueba",
                "cantidad": "1",
                "precio": "1000.00"
            }
        ]
    }


@pytest.fixture
def sample_document_data(test_db: Session, sample_extracted_data):
    """
    Crea un documento de prueba en la base de datos
    """
    from app.models.document import Document
    from datetime import datetime
    
    document = Document(
        filename="test_20241015_123456_invoice.pdf",
        original_filename="invoice.pdf",
        file_path="/uploads/test_20241015_123456_invoice.pdf",
        file_size=1024,
        mime_type="application/pdf",
        raw_text="FACTURA Test",
        extracted_data=sample_extracted_data,
        confidence_score=85,
        ocr_provider="tesseract",
        ocr_cost="0.00",
        processing_time="2.5s",
    )
    
    test_db.add(document)
    test_db.commit()
    test_db.refresh(document)
    
    return document


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def assert_valid_response():
    """
    Helper para validar respuestas de API
    """
    def _assert(response, status_code=200):
        assert response.status_code == status_code, \
            f"Expected {status_code}, got {response.status_code}: {response.text}"
        
        if status_code == 200:
            data = response.json()
            assert data is not None
            return data
        
        return response.json() if response.content else None
    
    return _assert


@pytest.fixture(autouse=True)
def cleanup_uploads(tmp_path):
    """
    Limpia archivos de upload después de cada test
    """
    yield
    
    # Cleanup
    upload_dir = Path(settings.UPLOAD_DIR)
    if upload_dir.exists():
        for file in upload_dir.glob("test_*"):
            try:
                file.unlink()
            except:
                pass


