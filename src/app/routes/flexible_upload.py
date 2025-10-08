"""
Ruta de upload flexible que permite elegir el método de procesamiento
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal
from enum import Enum
import os
import shutil
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document
from app.services.basic_extraction_service import get_basic_extraction_service
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

router = APIRouter()
logger = logging.getLogger(__name__)

class OCRMethod(str, Enum):
    """Métodos de OCR disponibles"""
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AUTO = "auto"  # Selección automática

class ExtractionMethod(str, Enum):
    """Métodos de extracción disponibles"""
    REGEX = "regex"
    SPACY = "spacy"
    LLM = "llm"
    HYBRID = "hybrid"  # Combina múltiples métodos
    AUTO = "auto"  # Selección automática

@router.post("/upload-flexible")
async def upload_document_flexible(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form("factura"),
    ocr_method: OCRMethod = Form(OCRMethod.AUTO),
    extraction_method: ExtractionMethod = Form(ExtractionMethod.AUTO),
    db: Session = Depends(get_db)
):
    """
    Subir y procesar documento con métodos seleccionables
    
    **Parámetros**:
    - **file**: Archivo PDF o imagen
    - **document_type**: Tipo (factura, recibo, contrato, etc.)
    - **ocr_method**: Método OCR a usar:
        - `tesseract`: OCR local gratuito
        - `google_vision`: Google Vision API (requiere configuración)
        - `aws_textract`: AWS Textract (requiere configuración)
        - `auto`: Selección automática según complejidad
    - **extraction_method**: Método de extracción:
        - `regex`: Patrones de expresiones regulares
        - `spacy`: Procesamiento con spaCy
        - `llm`: Extracción con LLM (requiere OpenAI)
        - `hybrid`: Combina múltiples métodos
        - `auto`: Selección automática
    
    **Respuesta**: Datos extraídos con información del método usado
    """
    try:
        # Validar y guardar archivo
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="El archivo no tiene nombre")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ".-_")
        filename = f"{timestamp}_{safe_filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"Archivo guardado: {filename} ({file_size} bytes)")
        
        # Paso 1: Extraer texto usando el método de OCR seleccionado
        ocr_result = await extract_text_with_method(
            file_path=file_path,
            content_type=file.content_type,
            method=ocr_method,
            document_type=document_type
        )
        
        if not ocr_result or not ocr_result.get("text"):
            raise HTTPException(
                status_code=400,
                detail=f"No se pudo extraer texto usando {ocr_method.value}"
            )
        
        # Paso 2: Extraer datos usando el método de extracción seleccionado
        extraction_result = await extract_data_with_method(
            text=ocr_result["text"],
            document_type=document_type,
            method=extraction_method
        )
        
        # Calcular confianza
        confidence = calculate_confidence_score(extraction_result, ocr_result)
        
        # Guardar en base de datos
        document = Document(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            raw_text=ocr_result["text"],
            extracted_data={
                "datos": extraction_result,
                "metodo_ocr": ocr_result.get("method"),
                "metodo_extraccion": extraction_result.get("method"),
                "confianza_ocr": ocr_result.get("confidence")
            },
            confidence_score=confidence,
            ocr_provider=ocr_result.get("method"),
            ocr_cost=str(ocr_result.get("cost", 0.0)),
            processing_time=f"{ocr_result.get('processing_time', 0):.2f}s"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "success": True,
            "document_id": document.id,
            "filename": filename,
            "file_size": file_size,
            "metodos_usados": {
                "ocr": ocr_result.get("method"),
                "extraccion": extraction_result.get("method"),
                "tiempo_total": f"{ocr_result.get('processing_time', 0):.2f}s"
            },
            "ocr_result": {
                "text_length": len(ocr_result["text"]),
                "confidence": ocr_result.get("confidence"),
                "cost": ocr_result.get("cost", 0.0)
            },
            "extracted_data": extraction_result.get("data", {}),
            "confidence": confidence,
            "message": "Documento procesado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando documento: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando documento: {str(e)}"
        )


async def extract_text_with_method(
    file_path: str,
    content_type: str,
    method: OCRMethod,
    document_type: str
) -> dict:
    """Extraer texto usando el método especificado"""
    
    import time
    start_time = time.time()
    
    try:
        # Decidir método automáticamente si es AUTO
        if method == OCRMethod.AUTO:
            method = await decide_best_ocr_method(file_path, document_type)
        
        # Ejecutar método seleccionado
        if method == OCRMethod.TESSERACT:
            result = await extract_with_tesseract(file_path, content_type)
        elif method == OCRMethod.GOOGLE_VISION:
            result = await extract_with_google_vision(file_path)
        elif method == OCRMethod.AWS_TEXTRACT:
            result = await extract_with_aws_textract(file_path)
        else:
            result = await extract_with_tesseract(file_path, content_type)
        
        result["processing_time"] = time.time() - start_time
        return result
        
    except Exception as e:
        logger.error(f"Error en OCR con método {method}: {e}")
        # Fallback a Tesseract si falla otro método
        if method != OCRMethod.TESSERACT:
            logger.info("Fallback a Tesseract")
            result = await extract_with_tesseract(file_path, content_type)
            result["processing_time"] = time.time() - start_time
            result["fallback"] = True
            return result
        raise


async def extract_data_with_method(
    text: str,
    document_type: str,
    method: ExtractionMethod
) -> dict:
    """Extraer datos usando el método especificado"""
    
    try:
        # Decidir método automáticamente si es AUTO
        if method == ExtractionMethod.AUTO:
            method = await decide_best_extraction_method(text, document_type)
        
        # Ejecutar método seleccionado
        if method == ExtractionMethod.REGEX:
            result = await extract_with_regex(text, document_type)
        elif method == ExtractionMethod.SPACY:
            result = await extract_with_spacy(text, document_type)
        elif method == ExtractionMethod.LLM:
            result = await extract_with_llm(text, document_type)
        elif method == ExtractionMethod.HYBRID:
            result = await extract_with_hybrid(text, document_type)
        else:
            result = await extract_with_hybrid(text, document_type)
        
        result["method"] = method.value
        return result
        
    except Exception as e:
        logger.error(f"Error en extracción con método {method}: {e}")
        # Fallback a regex si falla otro método
        if method != ExtractionMethod.REGEX:
            logger.info("Fallback a regex")
            result = await extract_with_regex(text, document_type)
            result["method"] = "regex_fallback"
            return result
        raise


# ==================== Métodos de OCR ====================

async def decide_best_ocr_method(file_path: str, document_type: str) -> OCRMethod:
    """Decidir automáticamente el mejor método de OCR"""
    # Por ahora, usar Tesseract siempre
    # En el futuro, analizar complejidad de la imagen
    return OCRMethod.TESSERACT


async def extract_with_tesseract(file_path: str, content_type: str) -> dict:
    """Extraer texto con Tesseract"""
    try:
        if content_type == "application/pdf":
            images = convert_from_path(file_path, dpi=300)
            text_parts = []
            for image in images:
                page_text = pytesseract.image_to_string(image, lang='spa')
                text_parts.append(page_text)
            text = "\n\n".join(text_parts)
        else:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='spa')
        
        return {
            "text": text,
            "method": "tesseract",
            "confidence": 0.75,
            "cost": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error con Tesseract: {str(e)}")


async def extract_with_google_vision(file_path: str) -> dict:
    """Extraer texto con Google Vision API"""
    try:
        from google.cloud import vision
        
        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
            raise HTTPException(
                status_code=400,
                detail="Google Vision API no configurada. Configura GOOGLE_APPLICATION_CREDENTIALS en .env"
            )
        
        client = vision.ImageAnnotatorClient()
        
        with open(file_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        text = ""
        if response.text_annotations:
            text = response.text_annotations[0].description
        
        return {
            "text": text,
            "method": "google_vision",
            "confidence": 0.95,
            "cost": 0.0015
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error con Google Vision: {str(e)}"
        )


async def extract_with_aws_textract(file_path: str) -> dict:
    """Extraer texto con AWS Textract"""
    try:
        import boto3
        
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise HTTPException(
                status_code=400,
                detail="AWS Textract no configurado. Configura AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en .env"
            )
        
        client = boto3.client(
            'textract',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        with open(file_path, 'rb') as document:
            response = client.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['TABLES', 'FORMS']
            )
        
        # Procesar respuesta
        text_blocks = []
        for block in response.get('Blocks', []):
            if block.get('BlockType') == 'LINE':
                text_blocks.append(block.get('Text', ''))
        
        text = '\n'.join(text_blocks)
        
        return {
            "text": text,
            "method": "aws_textract",
            "confidence": 0.92,
            "cost": 0.0015
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error con AWS Textract: {str(e)}"
        )


# ==================== Métodos de Extracción ====================

async def decide_best_extraction_method(text: str, document_type: str) -> ExtractionMethod:
    """Decidir automáticamente el mejor método de extracción"""
    # Si hay API de OpenAI configurada y el documento es complejo, usar LLM
    if settings.OPENAI_API_KEY and len(text) > 500:
        return ExtractionMethod.LLM
    # Si es documento simple, usar híbrido
    return ExtractionMethod.HYBRID


async def extract_with_regex(text: str, document_type: str) -> dict:
    """Extracción usando solo expresiones regulares"""
    import re
    
    data = {}
    
    # Patrones básicos
    patterns = {
        'numero_factura': r'(?:factura|invoice|fact\.|fac\.)\s*(?:n[°º]?|#)?\s*[:\-]?\s*([A-Z]?\d{4,}[\-/]?\d*)',
        'fecha': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        'cuit': r'(?:cuit|cuil)[:\s]*(\d{2}-\d{8}-\d{1})',
        'monto_total': r'(?:total)[:\s]*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'telefono': r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1) if match.groups() else match.group(0)
    
    return {
        "data": data,
        "method": "regex",
        "confidence": 0.65
    }


async def extract_with_spacy(text: str, document_type: str) -> dict:
    """Extracción usando spaCy"""
    extraction_service = get_basic_extraction_service()
    
    if not extraction_service.nlp:
        raise HTTPException(
            status_code=500,
            detail="spaCy no está disponible"
        )
    
    # Usar el servicio básico que ya tiene spaCy
    extracted = extraction_service.extract_data(text, document_type)
    
    return {
        "data": extracted,
        "method": "spacy",
        "confidence": 0.75
    }


async def extract_with_llm(text: str, document_type: str) -> dict:
    """Extracción usando LLM (OpenAI)"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API no configurada. Configura OPENAI_API_KEY en .env"
        )
    
    try:
        from app.services.intelligent_extraction_service import IntelligentExtractionService
        
        service = IntelligentExtractionService()
        result = await service.extract_intelligent_data(text)
        
        return {
            "data": result.structured_data if hasattr(result, 'structured_data') else {},
            "method": "llm_openai",
            "confidence": result.confidence if hasattr(result, 'confidence') else 0.85
        }
    except Exception as e:
        logger.error(f"Error con LLM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error con LLM: {str(e)}"
        )


async def extract_with_hybrid(text: str, document_type: str) -> dict:
    """Extracción híbrida (regex + spaCy)"""
    # Combinar regex y spaCy
    regex_result = await extract_with_regex(text, document_type)
    spacy_result = await extract_with_spacy(text, document_type)
    
    # Combinar resultados
    combined_data = {**regex_result["data"], **spacy_result["data"]}
    
    return {
        "data": combined_data,
        "method": "hybrid_regex_spacy",
        "confidence": 0.80
    }


def calculate_confidence_score(extraction_result: dict, ocr_result: dict) -> int:
    """Calcular score de confianza global"""
    ocr_confidence = ocr_result.get("confidence", 0.5)
    extraction_confidence = extraction_result.get("confidence", 0.5)
    
    # Contar campos extraídos
    data = extraction_result.get("data", {})
    fields_found = sum(1 for v in data.values() if v)
    
    # Combinar confianzas
    base_confidence = (ocr_confidence + extraction_confidence) / 2
    bonus = min(fields_found * 5, 30)  # Máximo 30 puntos de bonus
    
    return min(int(base_confidence * 70 + bonus), 100)


@router.get("/upload-flexible/methods")
async def get_available_methods():
    """
    Ver qué métodos están disponibles según la configuración
    """
    return {
        "ocr_methods": {
            "tesseract": {
                "available": True,
                "cost": "Gratis",
                "precision": "70-80%",
                "speed": "Rápido"
            },
            "google_vision": {
                "available": bool(settings.GOOGLE_APPLICATION_CREDENTIALS),
                "cost": "$1.50 por 1000 imágenes",
                "precision": "95-98%",
                "speed": "Medio",
                "requires": "GOOGLE_APPLICATION_CREDENTIALS en .env"
            },
            "aws_textract": {
                "available": bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY),
                "cost": "$1.50 por 1000 imágenes",
                "precision": "90-95%",
                "speed": "Medio",
                "requires": "AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en .env"
            },
            "auto": {
                "available": True,
                "description": "Selección automática según complejidad"
            }
        },
        "extraction_methods": {
            "regex": {
                "available": True,
                "description": "Patrones de expresiones regulares",
                "speed": "Muy rápido",
                "precision": "65-70%"
            },
            "spacy": {
                "available": True,
                "description": "Procesamiento con spaCy NLP",
                "speed": "Rápido",
                "precision": "75-80%"
            },
            "llm": {
                "available": bool(settings.OPENAI_API_KEY),
                "description": "Extracción con GPT",
                "speed": "Lento",
                "precision": "90-95%",
                "cost": "$0.002 por request",
                "requires": "OPENAI_API_KEY en .env"
            },
            "hybrid": {
                "available": True,
                "description": "Combina regex + spaCy",
                "speed": "Rápido",
                "precision": "80-85%"
            },
            "auto": {
                "available": True,
                "description": "Selección automática según configuración"
            }
        }
    }

