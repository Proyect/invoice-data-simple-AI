"""
Tests para Modelos
==================

Tests unitarios para los modelos del sistema.
"""
import pytest
from app.models.document import Document
from app.models.document_enhanced import DocumentType, DocumentStatus, OCRProvider
from app.repositories.document_repository import DocumentRepository
from app.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, MetadataMixin


@pytest.mark.unit
@pytest.mark.requires_db
class TestDocumentModel:
    """Tests para el modelo Document (document.py)"""
    
    @pytest.mark.unit
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
    
    @pytest.mark.unit
    @pytest.mark.requires_db
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
    
    @pytest.mark.unit
    @pytest.mark.requires_db
    def test_document_search_methods(self, sample_document, db_session):
        """Test métodos de búsqueda vía DocumentRepository"""
        repo = DocumentRepository(db_session)
        results = repo.search_by_text("FACTURA")
        assert len(results) >= 1
        assert any(d.id == sample_document.id for d in results)
        
        results = repo.get_by_type("factura")
        assert len(results) >= 1
        assert any(d.id == sample_document.id for d in results)
        
        results = repo.get_by_status("uploaded")
        assert len(results) >= 1
        assert any(d.id == sample_document.id for d in results)
    
    @pytest.mark.unit
    @pytest.mark.requires_db
    def test_document_stats(self, sample_document, db_session):
        """Test estadísticas de documentos vía DocumentRepository"""
        repo = DocumentRepository(db_session)
        stats = repo.get_stats()
        
        assert "total_documents" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "average_confidence" in stats
        
        assert stats["total_documents"] >= 1


@pytest.mark.unit
class TestBaseModel:
    """Tests para el modelo base"""
    
    @pytest.mark.unit
    def test_base_model_creation(self):
        """Test creación de modelo base"""
        class TestModelCreation(BaseModel):
            __tablename__ = "test_model_creation"
            name = "test"
        
        model = TestModelCreation()
        assert hasattr(model, "uuid")
        assert hasattr(model, "created_at")
        assert hasattr(model, "is_deleted")
        assert model.is_deleted is False or model.is_deleted is None  # puede ser None antes de flush
    
    def test_base_model_to_dict(self):
        """Test conversión a diccionario"""
        class TestModelToDict(BaseModel):
            __tablename__ = "test_model_to_dict"
            name = "test"
        
        model = TestModelToDict()
        model_dict = model.to_dict()
        
        assert "id" in model_dict
        assert "uuid" in model_dict
        assert "created_at" in model_dict
        assert "is_deleted" in model_dict


@pytest.mark.unit
class TestMixins:
    """Tests para los mixins"""
    
    @pytest.mark.unit
    def test_timestamp_mixin(self):
        """Test TimestampMixin"""
        class TestModelTimestamp(BaseModel, TimestampMixin):
            __tablename__ = "test_model_timestamp"
        
        model = TestModelTimestamp()
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
    
    def test_soft_delete_mixin(self):
        """Test SoftDeleteMixin"""
        class TestModelSoftDelete(BaseModel, SoftDeleteMixin):
            __tablename__ = "test_model_soft_delete"
        
        model = TestModelSoftDelete()
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        assert model.is_deleted is False or model.is_deleted is None
    
    def test_metadata_mixin(self):
        """Test MetadataMixin"""
        class TestModelMetadata(BaseModel, MetadataMixin):
            __tablename__ = "test_model_metadata"
        
        model = TestModelMetadata()
        assert hasattr(model, 'metadata_json')
        
        metadata = model.get_metadata()
        assert isinstance(metadata, dict)
        
        test_metadata = {"key": "value", "number": 123}
        model.set_metadata(test_metadata)
        assert model.get_metadata() == test_metadata
        
        model.update_metadata(new_key="new_value", number=456)
        expected = {"key": "value", "number": 456, "new_key": "new_value"}
        assert model.get_metadata() == expected


@pytest.mark.unit
class TestEnums:
    """Tests para los enums"""
    
    @pytest.mark.unit
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







