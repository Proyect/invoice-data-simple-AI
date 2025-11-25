# Sistema de Dependency Injection

## 📋 Resumen

Se ha implementado un sistema completo de **Dependency Injection (DI)** para mejorar la arquitectura, testabilidad y mantenibilidad del código.

## ✅ Cambios Implementados

### 1. Sistema de DI Centralizado

**Archivo**: `src/app/core/dependencies.py`

- **Providers**: Funciones que crean instancias de servicios
- **Container**: Contenedor opcional para casos avanzados
- **Cache**: Uso de `@lru_cache()` para servicios stateless

### 2. Servicios Refactorizados

Los siguientes servicios ahora aceptan dependencias inyectadas:

- ✅ `AFIPInvoiceExtractionService`
- ✅ `AsyncProcessingService`
- ✅ `BasicExtractionService`

**Antes:**
```python
class AFIPInvoiceExtractionService:
    def __init__(self):
        self.validation_service = AFIPValidationService()  # ❌ Acoplamiento
        self.specialized_ocr = SpecializedOCRService()
```

**Después:**
```python
class AFIPInvoiceExtractionService:
    def __init__(
        self,
        validation_service=None,  # ✅ Inyección opcional
        specialized_ocr=None,
        universal_validation=None
    ):
        # Inyectar o crear si no se proporcionan
        if validation_service is None:
            validation_service = AFIPValidationService()
        self.validation_service = validation_service
```

### 3. Endpoints Actualizados

**Archivos actualizados:**
- `src/app/api/v1/uploads.py`
- `src/app/routes/optimized_upload.py`
- `src/app/routes/uploads.py`

**Antes:**
```python
# Servicios globales (❌ difícil de testear)
processing_service = AsyncProcessingService()

@router.post("/upload")
async def upload(file: UploadFile, db: Session = Depends(get_db)):
    result = processing_service.process(...)  # ❌ Usa instancia global
```

**Después:**
```python
@router.post("/upload")
async def upload(
    file: UploadFile,
    db: Session = Depends(get_db),
    processing_service: AsyncProcessingService = Depends(get_async_processing_service)  # ✅ Inyectado
):
    result = processing_service.process(...)  # ✅ Usa instancia inyectada
```

## 🎯 Beneficios

### 1. **Testabilidad Mejorada**
```python
# Ahora puedes testear fácilmente con mocks
def test_upload():
    mock_service = Mock()
    mock_service.process.return_value = {"success": True}
    
    # Inyectar mock en el endpoint
    result = upload(file, db, processing_service=mock_service)
    assert result["success"] == True
```

### 2. **Desacoplamiento**
- Los servicios no crean sus dependencias directamente
- Fácil intercambiar implementaciones
- Mejor separación de responsabilidades

### 3. **Reutilización**
- Misma instancia de servicio compartida entre requests (con `@lru_cache()`)
- Menor overhead de creación de objetos

### 4. **Mantenibilidad**
- Cambios en servicios no afectan a los endpoints
- Fácil agregar nuevos servicios
- Código más limpio y organizado

## 📚 Uso

### Uso Básico en Endpoints

```python
from fastapi import Depends
from ..core.dependencies import (
    get_afip_invoice_extraction_service,
    get_optimal_ocr_service
)

@router.post("/process")
async def process_invoice(
    file: UploadFile,
    afip_service = Depends(get_afip_invoice_extraction_service),
    ocr_service = Depends(get_optimal_ocr_service)
):
    text = ocr_service.extract_text(file_path)
    data = afip_service.extract_afip_invoice_data(text)
    return data
```

### Testing con Mocks

```python
from unittest.mock import Mock

def test_afip_extraction():
    # Crear mocks
    mock_validation = Mock()
    mock_ocr = Mock()
    
    # Crear servicio con mocks
    service = AFIPInvoiceExtractionService(
        validation_service=mock_validation,
        specialized_ocr=mock_ocr
    )
    
    # Testear
    result = service.extract_afip_invoice_data("texto", "image.jpg")
    assert result is not None
```

### Uso del Container (Opcional)

```python
from ..core.dependencies import get_container

container = get_container()
afip_service = container.get('afip_invoice_extraction')
```

## 🔄 Migración

### Para Nuevos Endpoints

1. **Importar providers:**
```python
from ..core.dependencies import get_optimal_ocr_service
```

2. **Inyectar en función:**
```python
async def my_endpoint(
    ocr_service = Depends(get_optimal_ocr_service)
):
    # Usar servicio
    text = ocr_service.extract_text(...)
```

### Para Servicios Existentes

1. **Modificar `__init__` para aceptar dependencias:**
```python
def __init__(self, dependency=None):
    if dependency is None:
        dependency = DependencyService()
    self.dependency = dependency
```

2. **Crear provider en `dependencies.py`:**
```python
@lru_cache()
def get_my_service(dependency = Depends(get_dependency)):
    return MyService(dependency=dependency)
```

## 📊 Servicios Disponibles

| Servicio | Provider | Dependencias |
|----------|----------|--------------|
| `AFIPValidationService` | `get_afip_validation_service()` | Ninguna |
| `SpecializedOCRService` | `get_specialized_ocr_service()` | Ninguna |
| `OptimalOCRService` | `get_optimal_ocr_service()` | Ninguna |
| `IntelligentExtractionService` | `get_intelligent_extraction_service()` | Ninguna |
| `AFIPInvoiceExtractionService` | `get_afip_invoice_extraction_service()` | Validation, OCR, Universal |
| `AsyncProcessingService` | `get_async_processing_service()` | OCR, Extraction |
| `BasicExtractionService` | `get_basic_extraction_service()` | AFIP, Validation |
| `DocumentRepository` | `get_document_repository()` | DB Session |

## 🚀 Próximos Pasos

1. ✅ Sistema de DI implementado
2. ✅ Servicios principales refactorizados
3. ✅ Endpoints actualizados
4. ⏳ Actualizar tests para usar DI
5. ⏳ Documentar patrones de uso avanzados

## 📝 Notas

- Los servicios mantienen compatibilidad hacia atrás (crean instancias si no se inyectan)
- `@lru_cache()` se usa para servicios stateless (misma instancia por request)
- El container es opcional, FastAPI `Depends` es suficiente para la mayoría de casos

