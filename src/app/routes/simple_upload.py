"""
Ruta de upload simplificada sin dependencias de APIs externas
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
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

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Subir y procesar un documento (versión simplificada)
    
    - **file**: Archivo PDF o imagen
    - **document_type**: Tipo de documento (factura, recibo, etc.)
    """
    try:
        # Asegurar que el directorio de uploads existe
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Validar tipo de archivo
        if not file.content_type:
            raise HTTPException(status_code=400, detail="Tipo de archivo no válido")
        
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado: {file.content_type}"
            )
        
        # Validar que el archivo tenga nombre
        if not file.filename:
            raise HTTPException(status_code=400, detail="El archivo no tiene nombre")
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Limpiar el nombre del archivo de caracteres problemáticos
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ".-_")
        filename = f"{timestamp}_{safe_filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        logger.info(f"Guardando archivo: {file_path}")
        
        # Guardar archivo
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error guardando archivo: {str(e)}"
            )
        
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Archivo guardado: {filename} ({file_size} bytes)")
        
        # Extraer texto con OCR
        raw_text = await extract_text_from_file(file_path, file.content_type)
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer texto del documento. Verifica que sea legible."
            )
        
        logger.info(f"Texto extraído: {len(raw_text)} caracteres")
        
        # Extraer datos estructurados
        extraction_service = get_basic_extraction_service()
        extracted_data = extraction_service.extract_data(raw_text, document_type or "factura")
        
        logger.info(f"Datos extraídos: {list(extracted_data.keys())}")
        
        # Calcular confianza básica
        confidence = calculate_confidence(extracted_data)
        
        # Crear registro en base de datos
        document = Document(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            raw_text=raw_text,
            extracted_data=extracted_data,
            confidence_score=confidence,
            ocr_provider="tesseract",
            processing_time="local"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Documento creado con ID: {document.id}")
        
        return {
            "success": True,
            "document_id": document.id,
            "filename": filename,
            "file_size": file_size,
            "text_length": len(raw_text),
            "extracted_data": extracted_data,
            "confidence": confidence,
            "message": "Documento procesado exitosamente"
        }
        
    except HTTPException as e:
        # Re-lanzar HTTPException con el detalle original
        logger.error(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        # Capturar cualquier otro error y dar detalles completos
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"Error procesando documento: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando documento: {str(e)}"
        )


async def extract_text_from_file(file_path: str, content_type: str) -> str:
    """Extraer texto de un archivo usando Tesseract OCR"""
    try:
        if content_type == "application/pdf":
            # Convertir PDF a imágenes
            logger.info("Convirtiendo PDF a imágenes...")
            images = convert_from_path(file_path, dpi=300)
            
            # Extraer texto de cada página
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Procesando página {i+1}/{len(images)}")
                page_text = pytesseract.image_to_string(image, lang='spa')
                text_parts.append(page_text)
            
            return "\n\n--- Página {} ---\n\n".join(text_parts)
        
        else:
            # Procesar imagen directamente
            logger.info("Procesando imagen...")
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='spa')
            return text
    
    except Exception as e:
        logger.error(f"Error en OCR: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extrayendo texto: {str(e)}"
        )


def calculate_confidence(extracted_data: dict) -> int:
    """Calcular score de confianza basado en datos extraídos"""
    confidence = 0
    
    # Campos importantes para una factura
    important_fields = [
        "numero_factura",
        "fecha",
        "emisor",
        "receptor",
        "totales",
        "cuit"
    ]
    
    # Contar cuántos campos importantes se extrajeron
    for field in important_fields:
        if field in extracted_data and extracted_data[field]:
            confidence += 15
    
    # Bonus por items
    if "items" in extracted_data and extracted_data["items"]:
        confidence += 10
    
    # Limitar a 100
    return min(confidence, 100)


@router.get("/upload/test")
async def test_ocr():
    """Endpoint de prueba para verificar que OCR funciona"""
    try:
        # Verificar Tesseract
        version = pytesseract.get_tesseract_version()
        
        # Verificar modelo de spaCy
        extraction_service = get_basic_extraction_service()
        spacy_loaded = extraction_service.nlp is not None
        
        return {
            "tesseract_version": str(version),
            "spacy_loaded": spacy_loaded,
            "status": "OK" if spacy_loaded else "spaCy not loaded",
            "upload_dir": settings.UPLOAD_DIR,
            "upload_dir_exists": os.path.exists(settings.UPLOAD_DIR)
        }
    except Exception as e:
        return {
            "error": str(e),
            "tesseract_installed": False,
            "message": "Instala Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
        }

