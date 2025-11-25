"""
Upload Endpoints v1 (Legacy)
=============================

Endpoints legacy para compatibilidad con versiones anteriores.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.document import Document  # Usar el modelo básico de document.py
from ...schemas.document import ExtractedDataResponse
from ...services.async_processing_service import AsyncProcessingService
from ...services.optimal_ocr_service import OptimalOCRService
from ...services.intelligent_extraction_service import IntelligentExtractionService
from ...core.config import settings
import shutil
from pathlib import Path
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

# Servicios - Ahora usando Dependency Injection
from ...core.dependencies import (
    get_async_processing_service,
    get_optimal_ocr_service,
    get_intelligent_extraction_service
)


@router.post("/upload", response_model=ExtractedDataResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None, description="Tipo de documento (factura, recibo, contrato, formulario)"),
    db: Session = Depends(get_db),
    processing_service: AsyncProcessingService = Depends(get_async_processing_service),
    ocr_service: OptimalOCRService = Depends(get_optimal_ocr_service),
    extraction_service: IntelligentExtractionService = Depends(get_intelligent_extraction_service)
):
    """
    Sube documento y procesa con estrategia optimizada (método simple)
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Validar tipo de archivo
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Formatos permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Crear directorio si no existe
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        # Guardar archivo con nombre único para evitar colisiones
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro en base de datos
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            mime_type=file.content_type,
            status="pending",  # Estado inicial
            priority=5,  # Prioridad media por defecto
            language="es",  # Idioma español por defecto
            is_deleted=False  # No eliminado
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Procesar documento
        try:
            # Para archivos pequeños, procesamiento síncrono (ejecutar en thread para no bloquear)
            if file_path.stat().st_size < 5 * 1024 * 1024:  # 5MB
                import asyncio
                result = await asyncio.to_thread(
                    processing_service._process_document_worker,
                    str(file_path),
                    document_type,
                    db_document.id
                )
            else:
                # Para archivos grandes, procesamiento asíncrono
                job_id = await processing_service.process_document_async(str(file_path), document_type, db_document.id)
                result_obj = await processing_service.get_job_status(job_id)
                
                if result_obj.status.value == "failed":
                    raise HTTPException(status_code=500, detail=f"Error procesando documento: {result_obj.error}")
                
                result = result_obj.result
                if result is None:
                    raise HTTPException(status_code=500, detail="No se obtuvo resultado del procesamiento")
            
            # Actualizar documento con resultados
            # Siempre actualizar para asegurar que los datos estén guardados en la sesión actual
            # El worker puede haber actualizado, pero es mejor asegurarnos
            db_document.raw_text = result['ocr']['text']
            
            # Para facturas, guardar structured_data directamente como extracted_data
            extraction_data = result['extraction']
            if isinstance(extraction_data, dict):
                if extraction_data.get('document_type') == 'factura' and extraction_data.get('structured_data'):
                    # Si es factura y tiene structured_data, usar structured_data directamente
                    extracted_data = extraction_data['structured_data'].copy()
                    extracted_data['document_type'] = 'factura'
                    extracted_data['confidence'] = extraction_data.get('confidence', 0.8)
                    db_document.extracted_data = extracted_data
                else:
                    # Para otros casos, usar la estructura completa
                    db_document.extracted_data = extraction_data
            else:
                db_document.extracted_data = extraction_data
            
            db_document.confidence_score = int(result['extraction'].get('confidence', 0.8) * 100) if result['extraction'].get('confidence') else None
            db_document.ocr_provider = result['ocr'].get('provider', 'tesseract')
            # Convertir ocr_cost a float (la base de datos espera double precision)
            ocr_cost_value = result['ocr'].get('cost', 0)
            db_document.ocr_cost = float(ocr_cost_value) if ocr_cost_value is not None else 0.0
            # processing_time como string (VARCHAR)
            processing_time_value = result['ocr'].get('processing_time', 0)
            db_document.processing_time = str(processing_time_value) if processing_time_value is not None else "0"
            # Actualizar estado a completed
            if hasattr(db_document, 'status'):
                db_document.status = 'completed'
            
            db.commit()
            db.refresh(db_document)
            
            return ExtractedDataResponse(
                document_id=db_document.id,
                filename=db_document.original_filename,
                extracted_data=result['extraction'],
                raw_text=result['ocr']['text'],
                confidence_score=float(db_document.confidence_score) / 100.0 if db_document.confidence_score else None,
                ocr_provider=db_document.ocr_provider,
                processing_time=db_document.processing_time
            )
            
        except Exception as e:
            logger.error(f"Error procesando documento {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")


@router.post("/upload-flexible", response_model=ExtractedDataResponse)
async def upload_document_flexible(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None, description="Tipo de documento (factura, recibo, contrato, formulario)"),
    ocr_method: Optional[str] = Query("auto", description="Método OCR (auto, tesseract, google_vision, aws_textract)"),
    extraction_method: Optional[str] = Query("auto", description="Método de extracción (auto, regex, spacy, llm, hybrid)"),
    db: Session = Depends(get_db),
    ocr_service: OptimalOCRService = Depends(get_optimal_ocr_service),
    extraction_service: IntelligentExtractionService = Depends(get_intelligent_extraction_service)
):
    """
    Sube documento y procesa con opciones flexibles de OCR y extracción
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Validar tipo de archivo
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Formatos permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Crear directorio si no existe
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        # Guardar archivo con nombre único
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro en base de datos
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            mime_type=file.content_type,
            status="pending",  # Estado inicial
            priority=5,  # Prioridad media por defecto
            language="es",  # Idioma español por defecto
            is_deleted=False  # No eliminado
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Procesar documento con métodos específicos
        try:
            # Paso 1: OCR según método seleccionado
            if ocr_method == "tesseract" or ocr_method == "auto":
                ocr_text = ocr_service.extract_text(str(file_path), method="tesseract")
            else:
                # Para otros métodos, usar estrategia óptima
                ocr_result = await ocr_service.extract_text_optimal(str(file_path), document_type)
                ocr_text = ocr_result.text
            
            # Paso 2: Extracción según método seleccionado
            if extraction_method == "auto" or extraction_method == "hybrid":
                extraction_result = await extraction_service.extract_intelligent_data(ocr_text, str(file_path))
            else:
                # Extracción simple con regex (fallback)
                extraction_result = await extraction_service._fallback_extraction(ocr_text)
            
            # Paso 3: Combinar resultados
            result = {
                'ocr': {
                    'text': ocr_text,
                    'confidence': 0.8,
                    'provider': ocr_method if ocr_method != "auto" else "tesseract",
                    'cost': 0.0,
                    'processing_time': 0.0
                },
                'extraction': {
                    'document_type': extraction_result.document_type.value if hasattr(extraction_result.document_type, 'value') else str(extraction_result.document_type),
                    'confidence': extraction_result.confidence,
                    'entities': extraction_result.entities,
                    'structured_data': extraction_result.structured_data,
                    'metadata': extraction_result.metadata
                }
            }
            
            # Actualizar documento
            db_document.raw_text = ocr_text
            db_document.extracted_data = {
                'document_type': result['extraction']['document_type'],
                'confidence': result['extraction']['confidence'],
                'entities': result['extraction']['entities'],
                'structured_data': result['extraction']['structured_data']
            }
            db_document.confidence_score = int(result['extraction']['confidence'] * 100)
            db_document.ocr_provider = result['ocr']['provider']
            # Convertir ocr_cost a float (la base de datos espera double precision)
            ocr_cost_value = result['ocr'].get('cost', 0)
            db_document.ocr_cost = float(ocr_cost_value) if ocr_cost_value is not None else 0.0
            # processing_time como string (VARCHAR)
            processing_time_value = result['ocr'].get('processing_time', 0)
            db_document.processing_time = str(processing_time_value) if processing_time_value is not None else "0"
            # Actualizar estado a completed
            if hasattr(db_document, 'status'):
                db_document.status = 'completed'
            
            db.commit()
            db.refresh(db_document)
            
            return ExtractedDataResponse(
                document_id=db_document.id,
                filename=db_document.original_filename,
                extracted_data=result['extraction'],
                raw_text=ocr_text,
                confidence_score=float(db_document.confidence_score) / 100.0 if db_document.confidence_score else None,
                ocr_provider=db_document.ocr_provider,
                processing_time=db_document.processing_time
            )
            
        except Exception as e:
            logger.error(f"Error procesando documento {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")

