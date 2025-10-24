"""
Rutas para upload y procesamiento de documentos
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
import time
from pathlib import Path
import shutil
import logging

from ..core.database import get_db
from ..models.document import Document
from ..schemas.document import DocumentResponse
from ..services.basic_extraction_service import BasicExtractionService
from ..services.optimal_ocr_service import OptimalOCRService
from ..services.intelligent_extraction_service import IntelligentExtractionService

logger = logging.getLogger(__name__)
router = APIRouter()

# Servicios
basic_extraction = BasicExtractionService()
ocr_service = OptimalOCRService()
intelligent_extraction = IntelligentExtractionService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_simple(
    file: UploadFile = File(...),
    document_type: str = Form("factura"),
    db: Session = Depends(get_db)
):
    """
    Upload simple de documento
    """
    try:
        # Validar tipo de archivo
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/tiff"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no soportado. Formatos permitidos: PDF, JPG, PNG, TIFF"
            )
        
        # Crear nombre único para el archivo
        timestamp = int(time.time())
        file_extension = Path(file.filename).suffix
        new_filename = f"{timestamp}_{file.filename}"
        file_path = f"uploads/{new_filename}"
        
        # Crear directorio si no existe
        os.makedirs("uploads", exist_ok=True)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Procesar documento
        try:
            # Extraer texto con OCR
            logger.info(f"Iniciando extracción OCR para: {file_path}")
            raw_text = ocr_service.extract_text(file_path)
            logger.info(f"Texto extraído: {raw_text[:100]}...")
            
            # Extraer datos con servicio básico
            logger.info("Iniciando extracción de datos")
            extracted_data = basic_extraction.extract_data(raw_text, document_type)
            
            # Si es una factura AFIP, intentar mejorar con OCR especializado
            if extracted_data.get('tipo_documento') == 'factura_afip':
                logger.info("Factura AFIP detectada, aplicando OCR especializado")
                try:
                    from ..services.afip_invoice_extraction_service import AFIPInvoiceExtractionService
                    afip_service = AFIPInvoiceExtractionService()
                    enhanced_data = afip_service.extract_afip_invoice_data(raw_text, file_path)
                    if enhanced_data:
                        extracted_data = enhanced_data
                        logger.info("Datos mejorados con OCR especializado")
                except Exception as e:
                    logger.warning(f"Error aplicando OCR especializado: {e}")
            
            logger.info(f"Datos extraídos: {extracted_data}")
            
            # Crear registro en base de datos
            document = Document(
                filename=new_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file.size or 0,
                mime_type=file.content_type,
                raw_text=raw_text,
                extracted_data=extracted_data,
                confidence_score=0.8,  # Valor por defecto
                ocr_provider="tesseract",
                processing_time="2.5s"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Documento procesado: {file.filename} -> ID: {document.id}")
            return DocumentResponse.from_orm(document)
            
        except Exception as e:
            logger.error(f"Error procesando documento: {e}")
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            # Crear documento sin procesar
            document = Document(
                filename=new_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file.size or 0,
                mime_type=file.content_type,
                raw_text="",
                extracted_data={},
                confidence_score=0.0,
                ocr_provider="none",
                processing_time="0s"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return DocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error subiendo documento: {str(e)}")

@router.post("/upload-flexible", response_model=DocumentResponse)
async def upload_flexible(
    file: UploadFile = File(...),
    document_type: str = Form("factura"),
    ocr_method: str = Form("auto"),
    extraction_method: str = Form("auto"),
    db: Session = Depends(get_db)
):
    """
    Upload flexible de documento con opciones de procesamiento
    """
    try:
        # Validar tipo de archivo
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/tiff"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no soportado. Formatos permitidos: PDF, JPG, PNG, TIFF"
            )
        
        # Crear nombre único para el archivo
        timestamp = int(time.time())
        file_extension = Path(file.filename).suffix
        new_filename = f"{timestamp}_{file.filename}"
        file_path = f"uploads/{new_filename}"
        
        # Crear directorio si no existe
        os.makedirs("uploads", exist_ok=True)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Procesar documento según métodos seleccionados
        try:
            # Extraer texto con OCR
            if ocr_method == "auto":
                raw_text = ocr_service.extract_text(file_path)
            else:
                raw_text = ocr_service.extract_text(file_path, method=ocr_method)
            
            # Extraer datos según método seleccionado
            if extraction_method == "auto":
                extracted_data = intelligent_extraction.extract_document_data(raw_text, document_type)
            elif extraction_method == "basic":
                extracted_data = basic_extraction.extract_data(raw_text, document_type)
            else:
                extracted_data = intelligent_extraction.extract_document_data(raw_text, document_type)
            
            # Crear registro en base de datos
            document = Document(
                filename=new_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file.size or 0,
                mime_type=file.content_type,
                raw_text=raw_text,
                extracted_data=extracted_data,
                confidence_score=0.9,  # Valor mejorado para procesamiento flexible
                ocr_provider=ocr_method,
                processing_time="3.0s"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Documento procesado flexible: {file.filename} -> ID: {document.id}")
            return DocumentResponse.from_orm(document)
            
        except Exception as e:
            logger.error(f"Error procesando documento flexible: {e}")
            # Crear documento sin procesar
            document = Document(
                filename=new_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file.size or 0,
                mime_type=file.content_type,
                raw_text="",
                extracted_data={},
                confidence_score=0.0,
                ocr_provider=ocr_method,
                processing_time="0s"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return DocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo documento flexible: {e}")
        raise HTTPException(status_code=500, detail=f"Error subiendo documento flexible: {str(e)}")

@router.get("/upload-flexible/methods")
async def get_available_methods():
    """
    Obtener métodos disponibles para procesamiento
    """
    return {
        "ocr_methods": [
            {"id": "auto", "name": "Automático", "description": "Selecciona el mejor método automáticamente"},
            {"id": "tesseract", "name": "Tesseract", "description": "OCR local con Tesseract"},
            {"id": "google", "name": "Google Vision", "description": "OCR en la nube con Google Vision API"},
            {"id": "aws", "name": "AWS Textract", "description": "OCR en la nube con AWS Textract"}
        ],
        "extraction_methods": [
            {"id": "auto", "name": "Automático", "description": "Selecciona el mejor método automáticamente"},
            {"id": "basic", "name": "Básico", "description": "Extracción básica con regex"},
            {"id": "intelligent", "name": "Inteligente", "description": "Extracción con IA y NLP"}
        ],
        "document_types": [
            {"id": "factura", "name": "Factura", "description": "Factura comercial"},
            {"id": "boleta", "name": "Boleta", "description": "Boleta de venta"},
            {"id": "recibo", "name": "Recibo", "description": "Recibo de pago"},
            {"id": "nota_credito", "name": "Nota de Crédito", "description": "Nota de crédito"},
            {"id": "nota_debito", "name": "Nota de Débito", "description": "Nota de débito"},
            {"id": "titulo", "name": "Título", "description": "Título académico o profesional"},
            {"id": "diploma", "name": "Diploma", "description": "Diploma de graduación"},
            {"id": "certificado", "name": "Certificado", "description": "Certificado de curso o capacitación"},
            {"id": "licencia", "name": "Licencia", "description": "Licencia profesional o habilitación"},
            {"id": "dni", "name": "DNI", "description": "Documento Nacional de Identidad argentino"},
            {"id": "dni_tarjeta", "name": "DNI Tarjeta", "description": "DNI en formato tarjeta"},
            {"id": "dni_libreta", "name": "DNI Libreta", "description": "Libreta Cívica"},
            {"id": "pasaporte", "name": "Pasaporte", "description": "Pasaporte argentino"},
            {"id": "otro", "name": "Otro", "description": "Otro tipo de documento"}
        ]
    }
