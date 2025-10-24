"""
Tests para schemas Pydantic mejorados
Valida validaciones, conversiones y funcionalidades avanzadas
"""
import pytest
from datetime import datetime
from typing import Dict, Any

# Importar schemas mejorados
from src.app.schemas.document_enhanced import (
    DocumentEnhancedCreate,
    DocumentEnhancedUpdate,
    DocumentEnhancedResponse,
    DocumentTypeEnum,
    DocumentStatusEnum,
    OCRProviderEnum,
    ExtractionMethodEnum,
    DocumentLegacyToEnhanced,
    DocumentEnhancedToLegacy,
)

from src.app.schemas.user_enhanced import (
    UserEnhancedCreate,
    UserEnhancedUpdate,
    UserEnhancedResponse,
    UserRoleEnum,
    UserStatusEnum,
    AuthProviderEnum,
    UserLoginRequest,
    UserRegisterRequest,
    ChangePasswordRequest,
)

from src.app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationPlanEnum,
    OrganizationFeatureEnum,
)

from src.app.schemas.processing import (
    ProcessingJobCreate,
    ProcessingJobUpdate,
    ProcessingJobResponse,
    JobTypeEnum,
    JobStatusEnum,
    OCRJobConfiguration,
    ExtractionJobConfiguration,
)

# ============================================================================
# TESTS PARA SCHEMAS DE DOCUMENTOS
# ============================================================================

class TestDocumentEnhancedSchemas:
    """Tests para schemas de documentos mejorados"""
    
    def test_document_enhanced_create_valid(self):
        """Test crear documento con datos válidos"""
        doc_data = DocumentEnhancedCreate(
            filename="invoice_2024.pdf",
            original_filename="Factura_2024.pdf",
            file_path="/uploads/invoice_2024.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            document_type=DocumentTypeEnum.FACTURA,
            priority=3,
            language="es",
            tags=["factura", "2024", "urgente"]
        )
        
        assert doc_data.filename == "invoice_2024.pdf"
        assert doc_data.document_type == DocumentTypeEnum.FACTURA
        assert doc_data.priority == 3
        assert doc_data.tags == ["factura", "2024", "urgente"]
    
    def test_document_enhanced_create_invalid_filename(self):
        """Test validación de nombre de archivo inválido"""
        with pytest.raises(ValueError, match="caracteres peligrosos"):
            DocumentEnhancedCreate(
                filename="../../../etc/passwd",
                original_filename="test.pdf",
                file_path="/uploads/test.pdf"
            )
    
    def test_document_enhanced_create_invalid_tags(self):
        """Test validación de tags excesivos"""
        with pytest.raises(ValueError, match="más de 20 tags"):
            DocumentEnhancedCreate(
                filename="test.pdf",
                original_filename="test.pdf",
                file_path="/uploads/test.pdf",
                tags=[f"tag_{i}" for i in range(25)]  # 25 tags
            )
    
    def test_document_enhanced_update_partial(self):
        """Test actualización parcial de documento"""
        update_data = DocumentEnhancedUpdate(
            status=DocumentStatusEnum.PROCESSED,
            confidence_score=0.95
        )
        
        assert update_data.status == DocumentStatusEnum.PROCESSED
        assert update_data.confidence_score == 0.95
        assert update_data.filename is None  # No actualizado
    
    def test_document_enhanced_response_calculated_fields(self):
        """Test campos calculados en respuesta"""
        response = DocumentEnhancedResponse(
            id=1,
            uuid="test-uuid",
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            document_type=DocumentTypeEnum.FACTURA,
            status=DocumentStatusEnum.PROCESSED,
            priority=5,
            raw_text="Texto extraído",
            extracted_data={"total": 100.0},
            confidence_score=0.9,
            quality_score=0.8,
            ocr_provider=OCRProviderEnum.TESSERACT,
            extraction_method=ExtractionMethodEnum.SPACY,
            ocr_cost=0.0,
            processing_time_seconds=5.5,
            language="es",
            page_count=1,
            word_count=50,
            user_id=1,
            organization_id=1,
            reviewed_by=None,
            review_notes=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            processed_at=datetime.now(),
            reviewed_at=None,
            is_deleted=False,
            deleted_at=None,
            file_size_mb=1.0,
            is_processed=True,
            needs_review=False
        )
        
        assert response.file_size_mb == 1.0
        assert response.is_processed is True
        assert response.needs_review is False

# ============================================================================
# TESTS PARA SCHEMAS DE USUARIOS
# ============================================================================

class TestUserEnhancedSchemas:
    """Tests para schemas de usuarios mejorados"""
    
    def test_user_enhanced_create_valid(self):
        """Test crear usuario con datos válidos"""
        user_data = UserEnhancedCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User",
            role=UserRoleEnum.USER,
            organization_id=1
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.username == "testuser"  # Debe ser lowercase
        assert user_data.role == UserRoleEnum.USER
    
    def test_user_enhanced_create_invalid_password(self):
        """Test validación de contraseña débil"""
        with pytest.raises(ValueError, match="al menos 8 caracteres"):
            UserEnhancedCreate(
                email="test@example.com",
                username="testuser",
                password="123",  # Muy corta
                role=UserRoleEnum.USER
            )
        
        with pytest.raises(ValueError, match="letra minúscula"):
            UserEnhancedCreate(
                email="test@example.com",
                username="testuser",
                password="SECUREPASS123!",  # Sin minúsculas
                role=UserRoleEnum.USER
            )
        
        with pytest.raises(ValueError, match="letra mayúscula"):
            UserEnhancedCreate(
                email="test@example.com",
                username="testuser",
                password="securepass123!",  # Sin mayúsculas
                role=UserRoleEnum.USER
            )
        
        with pytest.raises(ValueError, match="número"):
            UserEnhancedCreate(
                email="test@example.com",
                username="testuser",
                password="SecurePass!",  # Sin números
                role=UserRoleEnum.USER
            )
        
        with pytest.raises(ValueError, match="carácter especial"):
            UserEnhancedCreate(
                email="test@example.com",
                username="testuser",
                password="SecurePass123",  # Sin caracteres especiales
                role=UserRoleEnum.USER
            )
    
    def test_user_enhanced_create_invalid_username(self):
        """Test validación de username inválido"""
        with pytest.raises(ValueError, match="3-30 caracteres"):
            UserEnhancedCreate(
                email="test@example.com",
                username="ab",  # Muy corto
                password="SecurePass123!",
                role=UserRoleEnum.USER
            )
    
    def test_user_login_request_valid(self):
        """Test request de login válido"""
        login_request = UserLoginRequest(
            username_or_email="test@example.com",
            password="SecurePass123!"
        )
        
        assert login_request.username_or_email == "test@example.com"  # Debe ser lowercase
    
    def test_user_register_request_passwords_match(self):
        """Test que las contraseñas coincidan en registro"""
        with pytest.raises(ValueError, match="no coinciden"):
            UserRegisterRequest(
                email="test@example.com",
                username="testuser",
                password="SecurePass123!",
                confirm_password="DifferentPass123!",
                terms_accepted=True,
                role=UserRoleEnum.USER
            )
    
    def test_change_password_request_validation(self):
        """Test validación de cambio de contraseña"""
        with pytest.raises(ValueError, match="no coinciden"):
            ChangePasswordRequest(
                current_password="OldPass123!",
                new_password="NewPass123!",
                confirm_password="DifferentPass123!"
            )

# ============================================================================
# TESTS PARA SCHEMAS DE ORGANIZACIONES
# ============================================================================

class TestOrganizationSchemas:
    """Tests para schemas de organizaciones"""
    
    def test_organization_create_valid(self):
        """Test crear organización válida"""
        org_data = OrganizationCreate(
            name="Test Organization",
            slug="test-org",
            description="Organización de prueba",
            plan=OrganizationPlanEnum.BASIC,
            features=[OrganizationFeatureEnum.DOCUMENT_PROCESSING, OrganizationFeatureEnum.API_ACCESS]
        )
        
        assert org_data.name == "Test Organization"
        assert org_data.slug == "test-org"  # Debe ser lowercase
        assert org_data.plan == OrganizationPlanEnum.BASIC
    
    def test_organization_create_invalid_slug(self):
        """Test validación de slug inválido"""
        with pytest.raises(ValueError, match="guión"):
            OrganizationCreate(
                name="Test Organization",
                slug="-invalid-slug",  # Empieza con guión
                description="Test"
            )
        
        with pytest.raises(ValueError, match="guión"):
            OrganizationCreate(
                name="Test Organization",
                slug="invalid-slug-",  # Termina con guión
                description="Test"
            )
        
        with pytest.raises(ValueError, match="solo puede contener"):
            OrganizationCreate(
                name="Test Organization",
                slug="invalid_slug!",  # Caracteres inválidos
                description="Test"
            )
    
    def test_organization_document_limit_validation(self):
        """Test validación de límites según plan"""
        with pytest.raises(ValueError, match="excede el permitido"):
            OrganizationCreate(
                name="Test Organization",
                slug="test-org",
                plan=OrganizationPlanEnum.FREE,
                document_limit=1000  # Excede límite del plan FREE (100)
            )

# ============================================================================
# TESTS PARA SCHEMAS DE PROCESAMIENTO
# ============================================================================

class TestProcessingSchemas:
    """Tests para schemas de procesamiento"""
    
    def test_processing_job_create_valid(self):
        """Test crear job de procesamiento válido"""
        job_data = ProcessingJobCreate(
            job_type=JobTypeEnum.DOCUMENT_OCR,
            document_id=1,
            priority=3,
            configuration={"language": "es", "preprocess": True}
        )
        
        assert job_data.job_type == JobTypeEnum.DOCUMENT_OCR
        assert job_data.document_id == 1
        assert job_data.priority == 3
    
    def test_processing_job_create_invalid_priority(self):
        """Test validación de prioridad inválida"""
        with pytest.raises(ValueError, match="entre 1 y 10"):
            ProcessingJobCreate(
                job_type=JobTypeEnum.DOCUMENT_OCR,
                priority=15  # Fuera de rango
            )
    
    def test_ocr_job_configuration_valid(self):
        """Test configuración de OCR válida"""
        config = OCRJobConfiguration(
            provider="tesseract",
            language="es",
            confidence_threshold=0.8,
            preprocess=True
        )
        
        assert config.provider == "tesseract"
        assert config.language == "es"
        assert config.confidence_threshold == 0.8
    
    def test_ocr_job_configuration_invalid_provider(self):
        """Test validación de proveedor OCR inválido"""
        with pytest.raises(ValueError):
            OCRJobConfiguration(
                provider="invalid_provider",
                language="es"
            )

# ============================================================================
# TESTS PARA CONVERSIÓN DE COMPATIBILIDAD
# ============================================================================

class TestCompatibilitySchemas:
    """Tests para schemas de compatibilidad"""
    
    def test_document_legacy_to_enhanced_valid(self):
        """Test conversión de documento legacy a mejorado"""
        legacy_doc = {
            "id": 1,
            "filename": "test.pdf",
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "raw_text": "Texto extraído",
            "extracted_data": {"total": 100.0},
            "confidence_score": 0.9,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        conversion = DocumentLegacyToEnhanced(
            legacy_document=legacy_doc,
            organization_id=1,
            user_id=1,
            tags=["test", "legacy"]
        )
        
        assert conversion.legacy_document["id"] == 1
        assert conversion.organization_id == 1
        assert conversion.tags == ["test", "legacy"]
    
    def test_document_legacy_to_enhanced_missing_fields(self):
        """Test conversión con campos faltantes"""
        legacy_doc = {
            "id": 1
            # Faltan campos requeridos
        }
        
        with pytest.raises(ValueError, match="Campo 'filename' es requerido"):
            DocumentLegacyToEnhanced(legacy_document=legacy_doc)
    
    def test_document_enhanced_to_legacy_conversion(self):
        """Test conversión de documento mejorado a legacy"""
        enhanced_doc = DocumentEnhancedResponse(
            id=1,
            uuid="test-uuid",
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            document_type=DocumentTypeEnum.FACTURA,
            status=DocumentStatusEnum.PROCESSED,
            priority=5,
            raw_text="Texto extraído",
            extracted_data={"total": 100.0},
            confidence_score=0.9,
            quality_score=0.8,
            ocr_provider=OCRProviderEnum.TESSERACT,
            extraction_method=ExtractionMethodEnum.SPACY,
            ocr_cost=0.0,
            processing_time_seconds=5.5,
            language="es",
            page_count=1,
            word_count=50,
            user_id=1,
            organization_id=1,
            reviewed_by=None,
            review_notes=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            processed_at=datetime.now(),
            reviewed_at=None,
            is_deleted=False,
            deleted_at=None,
            file_size_mb=1.0,
            is_processed=True,
            needs_review=False
        )
        
        conversion = DocumentEnhancedToLegacy(
            enhanced_document=enhanced_doc,
            include_extracted_data=True
        )
        
        legacy_dict = conversion.to_legacy_dict()
        
        assert legacy_dict["id"] == 1
        assert legacy_dict["filename"] == "test.pdf"
        assert legacy_dict["raw_text"] == "Texto extraído"
        assert legacy_dict["extracted_data"]["total"] == 100.0

# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================

class TestSchemaIntegration:
    """Tests de integración entre schemas"""
    
    def test_document_user_organization_relationship(self):
        """Test relación entre documentos, usuarios y organizaciones"""
        # Crear usuario
        user = UserEnhancedCreate(
            email="user@org.com",
            username="orguser",
            password="SecurePass123!",
            role=UserRoleEnum.USER,
            organization_id=1
        )
        
        # Crear organización
        org = OrganizationCreate(
            name="Test Org",
            slug="test-org",
            plan=OrganizationPlanEnum.BASIC
        )
        
        # Crear documento
        doc = DocumentEnhancedCreate(
            filename="org_document.pdf",
            original_filename="Org Document.pdf",
            file_path="/uploads/org_document.pdf",
            organization_id=1,
            user_id=1
        )
        
        # Verificar relaciones
        assert user.organization_id == 1
        assert doc.organization_id == 1
        assert doc.user_id == 1
    
    def test_processing_job_document_relationship(self):
        """Test relación entre jobs de procesamiento y documentos"""
        # Crear documento
        doc = DocumentEnhancedCreate(
            filename="process_doc.pdf",
            original_filename="Process Doc.pdf",
            file_path="/uploads/process_doc.pdf"
        )
        
        # Crear job de procesamiento
        job = ProcessingJobCreate(
            job_type=JobTypeEnum.DOCUMENT_OCR,
            document_id=1,
            configuration={"language": "es"}
        )
        
        # Verificar relación
        assert job.document_id == 1
        assert job.job_type == JobTypeEnum.DOCUMENT_OCR

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
