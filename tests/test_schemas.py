"""
Tests para Schemas
==================

Tests unitarios para los schemas del sistema.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from src.app.schemas.document_consolidated import (
    DocumentCreateSchema,
    DocumentUpdateSchema,
    DocumentResponseSchema,
    DocumentSearchRequestSchema,
    DocumentStatsResponseSchema,
    DocumentProcessingRequestSchema,
    DocumentReviewRequestSchema,
    DocumentBatchOperationRequestSchema,
    DocumentExportRequestSchema
)
from src.app.schemas.base import (
    BaseSchema,
    TimestampSchema,
    SoftDeleteSchema,
    MetadataSchema,
    PaginationSchema,
    SearchSchema,
    ResponseSchema,
    ErrorSchema,
    FileSchema,
    ConfidenceSchema,
    ProcessingSchema,
    TagsSchema,
    StatsSchema,
    BatchOperationSchema,
    ExportSchema
)


class TestDocumentSchemas:
    """Tests para schemas de documentos"""
    
    def test_document_create_schema_valid(self):
        """Test schema de creación válido"""
        data = {
            "filename": "test.pdf",
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "document_type": "factura",
            "language": "es",
            "priority": 5,
            "tags": ["urgente", "cliente-importante"]
        }
        
        schema = DocumentCreateSchema(**data)
        
        assert schema.filename == "test.pdf"
        assert schema.document_type == "factura"
        assert schema.language == "es"
        assert schema.priority == 5
        assert schema.tags == ["urgente", "cliente-importante"]
    
    def test_document_create_schema_invalid_filename(self):
        """Test schema de creación con nombre de archivo inválido"""
        data = {
            "filename": "",  # Nombre vacío
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreateSchema(**data)
        
        assert "El nombre del archivo no puede estar vacío" in str(exc_info.value)
    
    def test_document_create_schema_dangerous_filename(self):
        """Test schema de creación con nombre de archivo peligroso"""
        data = {
            "filename": "../../etc/passwd",  # Path traversal
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreateSchema(**data)
        
        assert "El nombre del archivo no puede contener" in str(exc_info.value)
    
    def test_document_create_schema_invalid_tags(self):
        """Test schema de creación con tags inválidos"""
        data = {
            "filename": "test.pdf",
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "tags": ["tag"] * 25  # Demasiados tags
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreateSchema(**data)
        
        assert "No se pueden tener más de 20 tags" in str(exc_info.value)
    
    def test_document_update_schema_valid(self):
        """Test schema de actualización válido"""
        data = {
            "document_type": "recibo",
            "status": "processed",
            "confidence_score": 0.95,
            "quality_score": 0.9,
            "tags": ["procesado", "validado"]
        }
        
        schema = DocumentUpdateSchema(**data)
        
        assert schema.document_type == "recibo"
        assert schema.status == "processed"
        assert schema.confidence_score == 0.95
        assert schema.quality_score == 0.9
        assert schema.tags == ["procesado", "validado"]
    
    def test_document_update_schema_invalid_confidence(self):
        """Test schema de actualización con confianza inválida"""
        data = {
            "confidence_score": 1.5  # Fuera del rango 0.0-1.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentUpdateSchema(**data)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    def test_document_search_schema_valid(self):
        """Test schema de búsqueda válido"""
        data = {
            "query": "factura",
            "document_type": "factura",
            "status": "processed",
            "min_confidence": 0.8,
            "max_confidence": 1.0,
            "date_from": datetime(2024, 1, 1),
            "date_to": datetime(2024, 12, 31),
            "tags": ["urgente"],
            "page": 1,
            "size": 20,
            "sort_by": "created_at",
            "sort_order": "desc"
        }
        
        schema = DocumentSearchRequestSchema(**data)
        
        assert schema.query == "factura"
        assert schema.document_type == "factura"
        assert schema.min_confidence == 0.8
        assert schema.max_confidence == 1.0
        assert schema.sort_by == "created_at"
        assert schema.sort_order == "desc"
    
    def test_document_search_schema_invalid_confidence_range(self):
        """Test schema de búsqueda con rango de confianza inválido"""
        data = {
            "min_confidence": 0.8,
            "max_confidence": 0.5  # max < min
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentSearchRequestSchema(**data)
        
        assert "max_confidence debe ser mayor o igual a min_confidence" in str(exc_info.value)
    
    def test_document_search_schema_invalid_date_range(self):
        """Test schema de búsqueda con rango de fechas inválido"""
        data = {
            "date_from": datetime(2024, 12, 31),
            "date_to": datetime(2024, 1, 1)  # date_to < date_from
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentSearchRequestSchema(**data)
        
        assert "date_to debe ser mayor o igual a date_from" in str(exc_info.value)
    
    def test_document_processing_request_schema_valid(self):
        """Test schema de solicitud de procesamiento válido"""
        data = {
            "document_id": 1,
            "ocr_provider": "tesseract",
            "extraction_method": "hybrid",
            "force_reprocess": True,
            "priority": 3
        }
        
        schema = DocumentProcessingRequestSchema(**data)
        
        assert schema.document_id == 1
        assert schema.ocr_provider == "tesseract"
        assert schema.extraction_method == "hybrid"
        assert schema.force_reprocess is True
        assert schema.priority == 3
    
    def test_document_review_request_schema_valid(self):
        """Test schema de solicitud de revisión válido"""
        data = {
            "document_id": 1,
            "action": "approve",
            "review_notes": "Documento aprobado",
            "confidence_override": 0.95
        }
        
        schema = DocumentReviewRequestSchema(**data)
        
        assert schema.document_id == 1
        assert schema.action == "approve"
        assert schema.review_notes == "Documento aprobado"
        assert schema.confidence_override == 0.95
    
    def test_document_review_request_schema_invalid_action(self):
        """Test schema de solicitud de revisión con acción inválida"""
        data = {
            "document_id": 1,
            "action": "invalid_action"  # Acción no válida
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentReviewRequestSchema(**data)
        
        assert "String should match pattern" in str(exc_info.value)
    
    def test_document_batch_operation_schema_valid(self):
        """Test schema de operación en lote válido"""
        data = {
            "document_ids": [1, 2, 3],
            "operation": "update_status",
            "parameters": {"status": "processed"}
        }
        
        schema = DocumentBatchOperationRequestSchema(**data)
        
        assert schema.document_ids == [1, 2, 3]
        assert schema.operation == "update_status"
        assert schema.parameters == {"status": "processed"}
    
    def test_document_batch_operation_schema_invalid_operation(self):
        """Test schema de operación en lote con operación inválida"""
        data = {
            "document_ids": [1, 2, 3],
            "operation": "invalid_operation"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentBatchOperationRequestSchema(**data)
        
        assert "Operación no válida" in str(exc_info.value)
    
    def test_document_export_request_schema_valid(self):
        """Test schema de solicitud de exportación válido"""
        data = {
            "document_ids": [1, 2, 3],
            "format": "json",
            "include_extracted_data": True,
            "include_raw_text": False,
            "date_from": datetime(2024, 1, 1),
            "date_to": datetime(2024, 12, 31)
        }
        
        schema = DocumentExportRequestSchema(**data)
        
        assert schema.document_ids == [1, 2, 3]
        assert schema.format == "json"
        assert schema.include_extracted_data is True
        assert schema.include_raw_text is False
    
    def test_document_export_request_schema_invalid_format(self):
        """Test schema de solicitud de exportación con formato inválido"""
        data = {
            "format": "invalid_format"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentExportRequestSchema(**data)
        
        assert "Formato no válido" in str(exc_info.value)


class TestBaseSchemas:
    """Tests para schemas base"""
    
    def test_file_schema_valid(self):
        """Test FileSchema válido"""
        data = {
            "filename": "test.pdf",
            "original_filename": "test.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf"
        }
        
        schema = FileSchema(**data)
        
        assert schema.filename == "test.pdf"
        assert schema.original_filename == "test.pdf"
        assert schema.file_size == 1024
        assert schema.mime_type == "application/pdf"
    
    def test_file_schema_invalid_filename(self):
        """Test FileSchema con nombre de archivo inválido"""
        data = {
            "filename": "../../etc/passwd",
            "original_filename": "test.pdf"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            FileSchema(**data)
        
        assert "El nombre del archivo no puede contener" in str(exc_info.value)
    
    def test_confidence_schema_valid(self):
        """Test ConfidenceSchema válido"""
        data = {
            "confidence_score": 0.95,
            "quality_score": 0.9
        }
        
        schema = ConfidenceSchema(**data)
        
        assert schema.confidence_score == 0.95
        assert schema.quality_score == 0.9
    
    def test_confidence_schema_invalid_range(self):
        """Test ConfidenceSchema con valores fuera de rango"""
        data = {
            "confidence_score": 1.5  # Fuera del rango 0.0-1.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConfidenceSchema(**data)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    def test_processing_schema_valid(self):
        """Test ProcessingSchema válido"""
        data = {
            "processing_time_seconds": 5.5,
            "ocr_cost": 0.01,
            "page_count": 2,
            "word_count": 150
        }
        
        schema = ProcessingSchema(**data)
        
        assert schema.processing_time_seconds == 5.5
        assert schema.ocr_cost == 0.01
        assert schema.page_count == 2
        assert schema.word_count == 150
    
    def test_tags_schema_valid(self):
        """Test TagsSchema válido"""
        data = {
            "tags": ["urgente", "cliente-importante", "factura"]
        }
        
        schema = TagsSchema(**data)
        
        assert schema.tags == ["urgente", "cliente-importante", "factura"]
    
    def test_tags_schema_invalid_too_many(self):
        """Test TagsSchema con demasiados tags"""
        data = {
            "tags": ["tag"] * 25  # Demasiados tags
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TagsSchema(**data)
        
        assert "No se pueden tener más de 20 tags" in str(exc_info.value)
    
    def test_tags_schema_invalid_empty(self):
        """Test TagsSchema con tags vacíos"""
        data = {
            "tags": ["", "valid_tag", "   "]  # Tags vacíos
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TagsSchema(**data)
        
        assert "Los tags no pueden estar vacíos" in str(exc_info.value)
    
    def test_pagination_schema_calculation(self):
        """Test cálculo automático de paginación"""
        data = {
            "page": 2,
            "size": 10,
            "total": 25
        }
        
        schema = PaginationSchema(**data)
        
        assert schema.page == 2
        assert schema.size == 10
        assert schema.total == 25
        assert schema.total_pages == 3  # (25 + 10 - 1) // 10
        assert schema.has_next is True
        assert schema.has_prev is True
    
    def test_stats_schema_valid(self):
        """Test StatsSchema válido"""
        data = {
            "total": 100,
            "by_category": {"factura": 50, "recibo": 30, "contrato": 20},
            "average_value": 0.85,
            "min_value": 0.1,
            "max_value": 1.0
        }
        
        schema = StatsSchema(**data)
        
        assert schema.total == 100
        assert schema.by_category == {"factura": 50, "recibo": 30, "contrato": 20}
        assert schema.average_value == 0.85
        assert schema.min_value == 0.1
        assert schema.max_value == 1.0
    
    def test_batch_operation_schema_valid(self):
        """Test BatchOperationSchema válido"""
        data = {
            "operation": "update_status",
            "item_ids": [1, 2, 3, 4, 5],
            "parameters": {"status": "processed"}
        }
        
        schema = BatchOperationSchema(**data)
        
        assert schema.operation == "update_status"
        assert schema.item_ids == [1, 2, 3, 4, 5]
        assert schema.parameters == {"status": "processed"}
    
    def test_batch_operation_schema_invalid_operation(self):
        """Test BatchOperationSchema con operación inválida"""
        data = {
            "operation": "invalid_operation",
            "item_ids": [1, 2, 3]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            BatchOperationSchema(**data)
        
        assert "Operación no válida" in str(exc_info.value)
    
    def test_export_schema_valid(self):
        """Test ExportSchema válido"""
        data = {
            "format": "json",
            "include_metadata": True,
            "include_raw_data": False,
            "date_from": datetime(2024, 1, 1),
            "date_to": datetime(2024, 12, 31)
        }
        
        schema = ExportSchema(**data)
        
        assert schema.format == "json"
        assert schema.include_metadata is True
        assert schema.include_raw_data is False
        assert schema.date_from == datetime(2024, 1, 1)
        assert schema.date_to == datetime(2024, 12, 31)
    
    def test_export_schema_invalid_format(self):
        """Test ExportSchema con formato inválido"""
        data = {
            "format": "invalid_format"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ExportSchema(**data)
        
        assert "Formato no válido" in str(exc_info.value)
    
    def test_export_schema_invalid_date_range(self):
        """Test ExportSchema con rango de fechas inválido"""
        data = {
            "format": "json",
            "date_from": datetime(2024, 12, 31),
            "date_to": datetime(2024, 1, 1)  # date_to < date_from
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ExportSchema(**data)
        
        assert "date_from debe ser anterior a date_to" in str(exc_info.value)





