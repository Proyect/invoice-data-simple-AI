"""
Tests para el endpoint de upload flexible
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestFlexibleUpload:
    """Tests para /api/v1/upload-flexible"""
    
    def test_upload_flexible_with_tesseract(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de upload flexible con método Tesseract"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload-flexible",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "document_type": "factura",
                    "ocr_method": "tesseract",
                    "extraction_method": "spacy"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["metodos_usados"]["ocr"] == "tesseract"
        assert "spacy" in data["metodos_usados"]["extraccion"]
    
    def test_upload_flexible_with_auto_method(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de upload flexible con método AUTO"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload-flexible",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "document_type": "factura",
                    "ocr_method": "auto",
                    "extraction_method": "auto"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "metodos_usados" in data
    
    def test_upload_flexible_regex_extraction(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        test_db: Session
    ):
        """Test de extracción con regex"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload-flexible",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "document_type": "factura",
                    "ocr_method": "tesseract",
                    "extraction_method": "regex"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted_data" in data
    
    def test_upload_flexible_hybrid_extraction(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de extracción híbrida"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload-flexible",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "document_type": "factura",
                    "ocr_method": "tesseract",
                    "extraction_method": "hybrid"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metodos_usados"]["extraccion"] == "hybrid_regex_spacy"
    
    def test_upload_flexible_returns_cost(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        test_db: Session
    ):
        """Test de que retorna información de costo"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload-flexible",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "ocr_method": "tesseract",
                    "extraction_method": "regex"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ocr_result" in data
        assert "cost" in data["ocr_result"]


class TestAvailableMethods:
    """Tests para el endpoint de métodos disponibles"""
    
    def test_get_available_methods(self, client: TestClient):
        """Test de listado de métodos disponibles"""
        response = client.get("/api/v1/upload-flexible/methods")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ocr_methods" in data
        assert "extraction_methods" in data
        
        # Verificar que Tesseract siempre está disponible
        assert data["ocr_methods"]["tesseract"]["available"] is True
        
        # Verificar métodos de extracción
        assert "regex" in data["extraction_methods"]
        assert "spacy" in data["extraction_methods"]
        assert "hybrid" in data["extraction_methods"]
    
    def test_available_methods_shows_requirements(self, client: TestClient):
        """Test de que muestra requirements para métodos no disponibles"""
        response = client.get("/api/v1/upload-flexible/methods")
        
        assert response.status_code == 200
        data = response.json()
        
        # Google Vision debería mostrar requirement
        google = data["ocr_methods"]["google_vision"]
        if not google["available"]:
            assert "requires" in google
        
        # LLM debería mostrar requirement
        llm = data["extraction_methods"]["llm"]
        if not llm["available"]:
            assert "requires" in llm


