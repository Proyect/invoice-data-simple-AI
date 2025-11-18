"""
Tests para Modelos
==================

Tests unitarios para los modelos del sistema.
"""
import pytest
from datetime import datetime
from src.app.models.document_unified import Document, DocumentType, DocumentStatus, OCRProvider
from src.app.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, MetadataMixin


class TestDocumentModel:
    """Tests para el modelo Document"""
    
    def test_document_creation(self, sample_document_data):
        """Test creación de documento"""
        document = Document(**sample_document_data)
        
        assert document.filename == "test_document.pdf"
        assert document.document_type == "factura"
        assert document.status == "uploaded"
        assert document.file_size == 1024
    
    def test_document_properties(self, sample_document):
        """Test propiedades calculadas"""
        # Test file_size_mb
        assert sample_document.file_size_mb == 0.0  # 1024 bytes = 0.001 MB, redondeado a 0.0
        
        # Test is_processed
        assert not sample_document.is_processed  # status = "uploaded"
        
        # Test needs_review
        assert not sample_document.needs_review  # confidence_score = None
    
    def test_document_json_data(self, sample_document):
        """Test manejo de datos JSON"""
        # Test extracted_data
        test_data = {"total": 100.0, "cliente": "Test Client"}
        sample_document.set_extracted_data(test_data)
        
        retrieved_data = sample_document.get_extracted_data()
        assert retrieved_data == test_data
        
        # Test tags
        test_tags = ["factura", "urgente", "cliente-importante"]
        sample_document.set_tags(test_tags)
        
        retrieved_tags = sample_document.get_tags()
        assert retrieved_tags == test_tags
        
        # Test add_tag
        sample_document.add_tag("nuevo-tag")
        assert "nuevo-tag" in sample_document.get_tags()
        
        # Test remove_tag
        sample_document.remove_tag("urgente")
        assert "urgente" not in sample_document.get_tags()
    
    def test_document_state_methods(self, sample_document, db_session):
        """Test métodos de estado"""
        # Test mark_processing
        sample_document.mark_processing(db_session)
        assert sample_document.status == DocumentStatus.PROCESSING.value
        
        # Test mark_processed
        sample_document.mark_processed(db_session, confidence_score=0.95)
        assert sample_document.status == DocumentStatus.PROCESSED.value
        assert sample_document.confidence_score == 0.95
        assert sample_document.processed_at is not None
        
        # Test mark_failed
        sample_document.mark_failed(db_session, "Error de procesamiento")
        assert sample_document.status == DocumentStatus.FAILED.value
        assert sample_document.review_notes == "Error de procesamiento"
    
    def test_document_search_methods(self, sample_document, db_session):
        """Test métodos de búsqueda"""
        # Test search_by_text
        results = Document.search_by_text(db_session, "FACTURA")
        assert len(results) >= 1
        assert sample_document in results
        
        # Test get_by_type
        results = Document.get_by_type(db_session, "factura")
        assert len(results) >= 1
        assert sample_document in results
        
        # Test get_by_status
        results = Document.get_by_status(db_session, "uploaded")
        assert len(results) >= 1
        assert sample_document in results
    
    def test_document_stats(self, sample_document, db_session):
        """Test estadísticas de documentos"""
        stats = Document.get_stats(db_session)
        
        assert "total_documents" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "average_confidence" in stats
        
        assert stats["total_documents"] >= 1


class TestBaseModel:
    """Tests para el modelo base"""
    
    def test_base_model_creation(self):
        """Test creación de modelo base"""
        # Crear una clase de prueba que herede de BaseModel
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            
            name = "test"
        
        model = TestModel()
        assert model.uuid is not None
        assert model.created_at is not None
        assert model.is_deleted is False
    
    def test_base_model_to_dict(self):
        """Test conversión a diccionario"""
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            
            name = "test"
        
        model = TestModel()
        model_dict = model.to_dict()
        
        assert "id" in model_dict
        assert "uuid" in model_dict
        assert "created_at" in model_dict
        assert "is_deleted" in model_dict


class TestMixins:
    """Tests para los mixins"""
    
    def test_timestamp_mixin(self):
        """Test TimestampMixin"""
        class TestModel(BaseModel, TimestampMixin):
            __tablename__ = "test_model"
        
        model = TestModel()
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
    
    def test_soft_delete_mixin(self):
        """Test SoftDeleteMixin"""
        class TestModel(BaseModel, SoftDeleteMixin):
            __tablename__ = "test_model"
        
        model = TestModel()
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        assert model.is_deleted is False
    
    def test_metadata_mixin(self):
        """Test MetadataMixin"""
        class TestModel(BaseModel, MetadataMixin):
            __tablename__ = "test_model"
        
        model = TestModel()
        assert hasattr(model, 'metadata_json')
        
        # Test get_metadata
        metadata = model.get_metadata()
        assert isinstance(metadata, dict)
        
        # Test set_metadata
        test_metadata = {"key": "value", "number": 123}
        model.set_metadata(test_metadata)
        assert model.get_metadata() == test_metadata
        
        # Test update_metadata
        model.update_metadata(new_key="new_value", number=456)
        expected = {"key": "value", "number": 456, "new_key": "new_value"}
        assert model.get_metadata() == expected


class TestEnums:
    """Tests para los enums"""
    
    def test_document_type_enum(self):
        """Test DocumentType enum"""
        assert DocumentType.FACTURA.value == "factura"
        assert DocumentType.RECIBO.value == "recibo"
        assert DocumentType.CONTRATO.value == "contrato"
    
    def test_document_status_enum(self):
        """Test DocumentStatus enum"""
        assert DocumentStatus.UPLOADED.value == "uploaded"
        assert DocumentStatus.PROCESSING.value == "processing"
        assert DocumentStatus.PROCESSED.value == "processed"
    
    def test_ocr_provider_enum(self):
        """Test OCRProvider enum"""
        assert OCRProvider.TESSERACT.value == "tesseract"
        assert OCRProvider.GOOGLE_VISION.value == "google_vision"
        assert OCRProvider.AWS_TEXTRACT.value == "aws_textract"





