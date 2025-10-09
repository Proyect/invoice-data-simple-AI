"""
Tests para los endpoints de gestión de documentos
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.document import Document


class TestDocumentsList:
    """Tests para listar documentos"""
    
    def test_list_documents_empty(self, client: TestClient, test_db: Session):
        """Test de lista vacía"""
        response = client.get("/api/v1/documents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["documents"]) == 0
    
    def test_list_documents_with_data(
        self,
        client: TestClient,
        sample_document_data,
        mock_redis
    ):
        """Test de lista con documentos"""
        response = client.get("/api/v1/documents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 1
        assert len(data["documents"]) == 1
        assert data["documents"][0]["id"] == sample_document_data.id
    
    def test_list_documents_pagination(
        self,
        client: TestClient,
        test_db: Session,
        sample_extracted_data
    ):
        """Test de paginación"""
        # Crear 15 documentos
        for i in range(15):
            doc = Document(
                filename=f"test_{i}.pdf",
                original_filename=f"original_{i}.pdf",
                file_path=f"/uploads/test_{i}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                extracted_data=sample_extracted_data
            )
            test_db.add(doc)
        test_db.commit()
        
        # Primera página (10 documentos)
        response = client.get("/api/v1/documents?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 10
        assert data["total"] == 15
        
        # Segunda página (5 documentos)
        response = client.get("/api/v1/documents?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 5
        assert data["total"] == 15


class TestDocumentGet:
    """Tests para obtener documento individual"""
    
    def test_get_document_success(self, client: TestClient, sample_document_data):
        """Test de obtener documento existente"""
        response = client.get(f"/api/v1/documents/{sample_document_data.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == sample_document_data.id
        assert data["filename"] == sample_document_data.filename
        assert "extracted_data" in data
    
    def test_get_document_not_found(self, client: TestClient, test_db: Session):
        """Test de documento no existente"""
        response = client.get("/api/v1/documents/99999")
        
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_get_document_text(self, client: TestClient, sample_document_data):
        """Test de obtener solo el texto de un documento"""
        response = client.get(f"/api/v1/documents/{sample_document_data.id}/text")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "raw_text" in data
        assert "confidence_score" in data
        assert data["document_id"] == sample_document_data.id
    
    def test_get_document_data(self, client: TestClient, sample_document_data):
        """Test de obtener solo datos extraídos"""
        response = client.get(f"/api/v1/documents/{sample_document_data.id}/data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted_data" in data
        assert data["document_id"] == sample_document_data.id


class TestDocumentDelete:
    """Tests para eliminar documentos"""
    
    def test_delete_document_success(
        self,
        client: TestClient,
        sample_document_data,
        mock_redis
    ):
        """Test de eliminación exitosa"""
        doc_id = sample_document_data.id
        
        response = client.delete(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == 200
        assert "eliminado" in response.json()["detail"].lower() or \
               "eliminado" in response.json().get("message", "").lower()
    
    def test_delete_document_not_found(self, client: TestClient, test_db: Session):
        """Test de eliminar documento inexistente"""
        response = client.delete("/api/v1/documents/99999")
        
        assert response.status_code == 404


class TestDocumentStats:
    """Tests para estadísticas de documentos"""
    
    def test_get_stats(
        self,
        client: TestClient,
        sample_document_data,
        mock_redis
    ):
        """Test de estadísticas"""
        response = client.get("/api/v1/documents/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_documents" in data
        assert "by_mime_type" in data
        assert "average_confidence" in data
    
    def test_stats_aggregates_correctly(
        self,
        client: TestClient,
        test_db: Session,
        sample_extracted_data,
        mock_redis
    ):
        """Test de que las agregaciones son correctas"""
        # Crear documentos con diferentes tipos
        doc1 = Document(
            filename="test1.pdf",
            original_filename="test1.pdf",
            file_path="/uploads/test1.pdf",
            file_size=1024,
            mime_type="application/pdf",
            confidence_score=80,
            extracted_data=sample_extracted_data
        )
        doc2 = Document(
            filename="test2.jpg",
            original_filename="test2.jpg",
            file_path="/uploads/test2.jpg",
            file_size=2048,
            mime_type="image/jpeg",
            confidence_score=90,
            extracted_data=sample_extracted_data
        )
        test_db.add(doc1)
        test_db.add(doc2)
        test_db.commit()
        
        response = client.get("/api/v1/documents/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_documents"] == 2
        assert len(data["by_mime_type"]) == 2
        assert 80 <= data["average_confidence"] <= 90


class TestHealthAndInfo:
    """Tests para endpoints de salud e información"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test del endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self, client: TestClient):
        """Test del health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
    
    def test_info_endpoint(self, client: TestClient):
        """Test del endpoint de información"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        
        assert "app_name" in data
        assert "version" in data
        assert "features" in data


