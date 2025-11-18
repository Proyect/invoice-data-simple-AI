"""
Tests para Repositories
=======================

Tests unitarios para los repositories del sistema.
"""
import pytest
from unittest.mock import Mock, patch
from src.app.repositories.document_repository import DocumentRepository
from src.app.models.document_unified import Document, DocumentType, DocumentStatus


class TestDocumentRepository:
    """Tests para DocumentRepository"""
    
    def test_create_document(self, document_repository, sample_document_data):
        """Test creación de documento"""
        document = document_repository.create(**sample_document_data)
        
        assert document.id is not None
        assert document.filename == sample_document_data["filename"]
        assert document.document_type == sample_document_data["document_type"]
    
    def test_get_by_id(self, document_repository, sample_document):
        """Test obtener documento por ID"""
        found_document = document_repository.get_by_id(sample_document.id)
        
        assert found_document is not None
        assert found_document.id == sample_document.id
        assert found_document.filename == sample_document.filename
    
    def test_get_by_id_not_found(self, document_repository):
        """Test obtener documento inexistente"""
        found_document = document_repository.get_by_id(99999)
        assert found_document is None
    
    def test_get_all(self, document_repository, sample_document):
        """Test obtener todos los documentos"""
        documents = document_repository.get_all(limit=10)
        
        assert isinstance(documents, list)
        assert len(documents) >= 1
        assert sample_document in documents
    
    def test_update_document(self, document_repository, sample_document):
        """Test actualización de documento"""
        updated_document = document_repository.update(
            sample_document.id,
            confidence_score=0.95,
            status=DocumentStatus.PROCESSED.value
        )
        
        assert updated_document is not None
        assert updated_document.confidence_score == 0.95
        assert updated_document.status == DocumentStatus.PROCESSED.value
    
    def test_delete_document(self, document_repository, sample_document):
        """Test eliminación de documento"""
        success = document_repository.delete(sample_document.id)
        assert success is True
        
        # Verificar que el documento fue eliminado
        found_document = document_repository.get_by_id(sample_document.id)
        assert found_document is None
    
    def test_count_documents(self, document_repository, sample_document):
        """Test conteo de documentos"""
        count = document_repository.count()
        assert count >= 1
        
        # Test con filtros
        count_by_type = document_repository.count(document_type="factura")
        assert count_by_type >= 1
    
    def test_exists_document(self, document_repository, sample_document):
        """Test verificar existencia de documento"""
        exists = document_repository.exists(sample_document.id)
        assert exists is True
        
        exists_false = document_repository.exists(99999)
        assert exists_false is False
    
    def test_search_by_text(self, document_repository, sample_document):
        """Test búsqueda por texto"""
        results = document_repository.search_by_text("FACTURA")
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_get_by_type(self, document_repository, sample_document):
        """Test obtener por tipo"""
        results = document_repository.get_by_type("factura")
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_get_by_status(self, document_repository, sample_document):
        """Test obtener por estado"""
        results = document_repository.get_by_status("uploaded")
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_advanced_search(self, document_repository, sample_document):
        """Test búsqueda avanzada"""
        results = document_repository.advanced_search(
            query="FACTURA",
            document_type="factura",
            status="uploaded",
            limit=10
        )
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_get_stats(self, document_repository, sample_document):
        """Test estadísticas"""
        stats = document_repository.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_documents" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "average_confidence" in stats
        
        assert stats["total_documents"] >= 1
    
    def test_mark_processing(self, document_repository, sample_document):
        """Test marcar como procesando"""
        success = document_repository.mark_processing(sample_document.id)
        assert success is True
        
        # Verificar que el estado cambió
        updated_document = document_repository.get_by_id(sample_document.id)
        assert updated_document.status == DocumentStatus.PROCESSING.value
    
    def test_mark_processed(self, document_repository, sample_document):
        """Test marcar como procesado"""
        success = document_repository.mark_processed(
            sample_document.id,
            confidence_score=0.95,
            extracted_data={"total": 100.0},
            processing_time=5.5
        )
        assert success is True
        
        # Verificar que el estado y datos cambiaron
        updated_document = document_repository.get_by_id(sample_document.id)
        assert updated_document.status == DocumentStatus.PROCESSED.value
        assert updated_document.confidence_score == 0.95
        assert updated_document.processed_at is not None
    
    def test_mark_failed(self, document_repository, sample_document):
        """Test marcar como fallido"""
        error_message = "Error de procesamiento"
        success = document_repository.mark_failed(sample_document.id, error_message)
        assert success is True
        
        # Verificar que el estado cambió
        updated_document = document_repository.get_by_id(sample_document.id)
        assert updated_document.status == DocumentStatus.FAILED.value
        assert updated_document.review_notes == error_message
    
    def test_approve_document(self, document_repository, sample_document):
        """Test aprobar documento"""
        reviewed_by = 1
        notes = "Documento aprobado"
        success = document_repository.approve(sample_document.id, reviewed_by, notes)
        assert success is True
        
        # Verificar que el estado cambió
        updated_document = document_repository.get_by_id(sample_document.id)
        assert updated_document.status == DocumentStatus.APPROVED.value
        assert updated_document.reviewed_by == reviewed_by
        assert updated_document.review_notes == notes
    
    def test_reject_document(self, document_repository, sample_document):
        """Test rechazar documento"""
        reviewed_by = 1
        reason = "Documento rechazado por calidad"
        success = document_repository.reject(sample_document.id, reviewed_by, reason)
        assert success is True
        
        # Verificar que el estado cambió
        updated_document = document_repository.get_by_id(sample_document.id)
        assert updated_document.status == DocumentStatus.REJECTED.value
        assert updated_document.reviewed_by == reviewed_by
        assert updated_document.review_notes == reason
    
    def test_get_recent_documents(self, document_repository, sample_document):
        """Test obtener documentos recientes"""
        results = document_repository.get_recent(days=7)
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_get_high_confidence_documents(self, document_repository, sample_document):
        """Test obtener documentos con alta confianza"""
        # Primero marcar como procesado con alta confianza
        document_repository.mark_processed(sample_document.id, confidence_score=0.95)
        
        results = document_repository.get_high_confidence(min_confidence=0.9)
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert sample_document in results
    
    def test_bulk_operations(self, document_repository):
        """Test operaciones en lote"""
        # Crear múltiples documentos
        documents_data = [
            {
                "filename": f"test_doc_{i}.pdf",
                "original_filename": f"test_doc_{i}.pdf",
                "file_path": f"/uploads/test_doc_{i}.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf",
                "document_type": "factura",
                "status": "uploaded"
            }
            for i in range(3)
        ]
        
        # Test bulk create
        created_documents = document_repository.bulk_create(documents_data)
        assert len(created_documents) == 3
        
        # Test bulk update
        updates = [
            {"id": doc.id, "confidence_score": 0.9}
            for doc in created_documents
        ]
        updated_count = document_repository.bulk_update(updates)
        assert updated_count == 3
        
        # Test bulk delete
        document_ids = [doc.id for doc in created_documents]
        deleted_count = document_repository.bulk_delete(document_ids)
        assert deleted_count == 3





