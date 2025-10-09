"""
Tests para el endpoint de upload simple
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from io import BytesIO


class TestSimpleUpload:
    """Tests para /api/v1/upload"""
    
    def test_upload_pdf_success(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de upload exitoso de PDF"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test_invoice.pdf", f, "application/pdf")},
                data={"document_type": "factura"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "document_id" in data
        assert data["filename"].endswith(".pdf")
        assert "extracted_data" in data
        assert data["confidence"] > 0
    
    def test_upload_image_success(
        self,
        client: TestClient,
        sample_image_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de upload exitoso de imagen"""
        with open(sample_image_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test_invoice.jpg", f, "image/jpeg")},
                data={"document_type": "factura"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "document_id" in data
    
    def test_upload_invalid_file_type(self, client: TestClient):
        """Test de rechazo de tipo de archivo inválido"""
        file_content = b"fake content"
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
            data={"document_type": "factura"}
        )
        
        assert response.status_code == 400
        assert "no soportado" in response.json()["detail"].lower()
    
    def test_upload_without_file(self, client: TestClient):
        """Test de request sin archivo"""
        response = client.post(
            "/api/v1/upload",
            data={"document_type": "factura"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_extracts_invoice_data(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de extracción correcta de datos de factura"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={"document_type": "factura"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        extracted = data["extracted_data"]
        assert "numero_factura" in extracted
        assert "fecha" in extracted
    
    def test_upload_saves_to_database(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de que el documento se guarda en la BD"""
        from app.models.document import Document
        
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("invoice.pdf", f, "application/pdf")},
            )
        
        assert response.status_code == 200
        doc_id = response.json()["document_id"]
        
        # Verificar en BD
        doc = test_db.query(Document).filter(Document.id == doc_id).first()
        assert doc is not None
        assert doc.filename is not None
        assert doc.raw_text is not None
    
    def test_upload_calculates_confidence(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy,
        test_db: Session
    ):
        """Test de cálculo de confianza"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("invoice.pdf", f, "application/pdf")},
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 100


class TestOCREndpoint:
    """Tests para el endpoint de test de OCR"""
    
    def test_ocr_test_endpoint(self, client: TestClient, mock_tesseract, mock_spacy):
        """Test del endpoint /api/v1/upload/test"""
        response = client.get("/api/v1/upload/test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tesseract_version" in data
        assert "spacy_loaded" in data
        assert "status" in data


