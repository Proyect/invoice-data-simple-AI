"""
Tests para los servicios de extracción y procesamiento
"""
import pytest
from app.services.basic_extraction_service import BasicExtractionService


class TestBasicExtractionService:
    """Tests para el servicio de extracción básica"""
    
    @pytest.fixture
    def extraction_service(self, mock_spacy):
        """Fixture del servicio de extracción"""
        return BasicExtractionService()
    
    def test_extract_invoice_number(self, extraction_service):
        """Test de extracción de número de factura"""
        text = "FACTURA N° 0001-00000123"
        data = extraction_service.extract_data(text, "factura")
        
        assert "numero_factura" in data
        assert "0001-00000123" in data["numero_factura"]
    
    def test_extract_date(self, extraction_service):
        """Test de extracción de fecha"""
        text = "Fecha: 15/10/2024"
        data = extraction_service.extract_data(text, "factura")
        
        assert "fecha" in data
        assert "15/10/2024" in data["fecha"]
    
    def test_extract_cuit(self, extraction_service):
        """Test de extracción de CUIT"""
        text = "CUIT: 20-12345678-9"
        data = extraction_service.extract_data(text, "factura")
        
        assert "cuit" in data
        assert data["cuit"] == "20-12345678-9"
    
    def test_extract_amounts(self, extraction_service):
        """Test de extracción de montos"""
        text = "Subtotal: $1,000.00\nIVA: $210.00\nTotal: $1,234.56"
        data = extraction_service.extract_data(text, "factura")
        
        assert "totales" in data
        totals = data["totales"]
        assert "total" in totals
    
    def test_extract_email(self, extraction_service):
        """Test de extracción de email"""
        text = "Contacto: test@example.com"
        result = extraction_service._extract_emails(text)
        
        assert len(result) > 0
        assert "test@example.com" in result
    
    def test_extract_phone(self, extraction_service):
        """Test de extracción de teléfono"""
        text = "Teléfono: (011) 1234-5678"
        result = extraction_service._extract_phones(text)
        
        assert len(result) > 0
    
    def test_detect_document_type_invoice(self, extraction_service):
        """Test de detección de tipo de documento - factura"""
        text = "FACTURA A\nNúmero: 001-00000123"
        doc_type = extraction_service._detect_document_type(text)
        
        assert doc_type == "factura"
    
    def test_detect_document_type_receipt(self, extraction_service):
        """Test de detección de tipo de documento - recibo"""
        text = "RECIBO DE PAGO\nNúmero: 001"
        doc_type = extraction_service._detect_document_type(text)
        
        assert doc_type == "recibo"
    
    def test_extract_iva_condition(self, extraction_service):
        """Test de extracción de condición ante IVA"""
        text = "Condición ante IVA: Responsable Inscripto"
        result = extraction_service._extract_iva_condition(text)
        
        assert result is not None
        assert "Responsable Inscripto" in result
    
    def test_handles_empty_text(self, extraction_service):
        """Test de manejo de texto vacío"""
        result = extraction_service.extract_data("", "factura")
        
        assert "error" in result
    
    def test_handles_none_text(self, extraction_service):
        """Test de manejo de None"""
        result = extraction_service.extract_data(None, "factura")
        
        assert "error" in result


class TestCacheService:
    """Tests para el servicio de cache"""
    
    @pytest.fixture
    def cache_service(self, mock_redis):
        """Fixture del servicio de cache"""
        from app.services.cache_service import CacheService
        return CacheService()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service):
        """Test de set y get básico"""
        await cache_service.set("test_key", "test_value")
        value = await cache_service.get("test_key")
        
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_service):
        """Test de get de clave inexistente"""
        value = await cache_service.get("nonexistent_key")
        
        assert value is None
    
    @pytest.mark.asyncio
    async def test_delete_key(self, cache_service):
        """Test de eliminación de clave"""
        await cache_service.set("test_key", "test_value")
        await cache_service.delete("test_key")
        
        value = await cache_service.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache_service):
        """Test de set con TTL"""
        result = await cache_service.set("test_key", "test_value", ttl=60)
        
        assert result is True or result is not None
    
    @pytest.mark.asyncio
    async def test_cache_complex_object(self, cache_service):
        """Test de cacheo de objeto complejo"""
        data = {
            "field1": "value1",
            "field2": 123,
            "field3": [1, 2, 3],
            "field4": {"nested": "object"}
        }
        
        await cache_service.set("complex_key", data)
        retrieved = await cache_service.get("complex_key")
        
        assert retrieved == data


class TestIntelligentExtraction:
    """Tests para el servicio de extracción inteligente"""
    
    @pytest.fixture
    def intelligent_service(self, mock_spacy, mock_openai):
        """Fixture del servicio inteligente"""
        from app.services.intelligent_extraction_service import IntelligentExtractionService
        return IntelligentExtractionService()
    
    def test_detect_factura_type(self, intelligent_service):
        """Test de detección de tipo factura"""
        from app.services.intelligent_extraction_service import DocumentType
        
        text = "FACTURA A N° 0001-00000123"
        doc_type = intelligent_service._detect_document_type(text)
        
        assert doc_type == DocumentType.FACTURA
    
    def test_detect_recibo_type(self, intelligent_service):
        """Test de detección de tipo recibo"""
        from app.services.intelligent_extraction_service import DocumentType
        
        text = "RECIBO DE PAGO N° 001"
        doc_type = intelligent_service._detect_document_type(text)
        
        assert doc_type == DocumentType.RECIBO
    
    @pytest.mark.asyncio
    async def test_extract_with_spacy(self, intelligent_service):
        """Test de extracción con spaCy"""
        text = "Test Company SA ubicada en Buenos Aires"
        result = await intelligent_service._extract_with_spacy(text)
        
        assert result["method"] == "spacy"
        assert "data" in result
        assert result["confidence"] > 0
    
    def test_regex_extraction(self, intelligent_service):
        """Test de extracción con regex"""
        text = "Fecha: 15/10/2024\nCUIT: 20-12345678-9\nEmail: test@example.com"
        result = intelligent_service._extract_with_regex(text)
        
        assert len(result) > 0
        assert any(key in result for key in ["fecha", "cuit", "email"])
    
    @pytest.mark.asyncio
    async def test_extract_intelligent_data(self, intelligent_service):
        """Test de extracción inteligente completa"""
        text = """
        FACTURA A
        Número: 0001-00000123
        Fecha: 15/10/2024
        Emisor: Test Company SA
        CUIT: 20-12345678-9
        Total: $1,234.56
        """
        
        result = await intelligent_service.extract_intelligent_data(text)
        
        assert result is not None
        assert result.confidence > 0
        assert result.structured_data is not None


class TestOptimalOCR:
    """Tests para el servicio de OCR óptimo"""
    
    @pytest.fixture
    def ocr_service(self, mock_tesseract):
        """Fixture del servicio de OCR"""
        from app.services.optimal_ocr_service import OptimalOCRService
        return OptimalOCRService()
    
    @pytest.mark.asyncio
    async def test_tesseract_extraction(self, ocr_service, sample_image_path):
        """Test de extracción con Tesseract"""
        result = await ocr_service._use_tesseract(str(sample_image_path))
        
        assert result.text is not None
        assert result.provider == "tesseract"
        assert result.cost == 0.0
        assert 0 <= result.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_clean_text(self, ocr_service):
        """Test de limpieza de texto"""
        dirty_text = "  Test   text   with    extra    spaces  \n\n\n"
        clean = ocr_service._clean_text(dirty_text)
        
        assert clean == "Test text with extra spaces"
    
    @pytest.mark.asyncio
    async def test_analyze_complexity(self, ocr_service, sample_image_path):
        """Test de análisis de complejidad"""
        from app.services.optimal_ocr_service import DocumentComplexity
        
        complexity = await ocr_service._analyze_document_complexity(str(sample_image_path))
        
        assert complexity in [
            DocumentComplexity.SIMPLE,
            DocumentComplexity.MEDIUM,
            DocumentComplexity.COMPLEX
        ]
    
    @pytest.mark.asyncio
    async def test_select_optimal_strategy(self, ocr_service):
        """Test de selección de estrategia óptima"""
        from app.services.optimal_ocr_service import DocumentComplexity
        
        # Documento simple debería usar Tesseract
        strategy = ocr_service._select_optimal_strategy(
            DocumentComplexity.SIMPLE,
            "factura"
        )
        assert strategy == "tesseract"




