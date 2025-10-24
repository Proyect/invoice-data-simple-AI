from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.document import Document
from ..schemas.document import DocumentResponse, ExtractedDataResponse
from ..services.async_processing_service import AsyncProcessingService
from ..services.cache_service import cache_service
from ..core.config import settings
import shutil
from pathlib import Path
import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)
router = APIRouter()

# Servicios
processing_service = AsyncProcessingService()

@router.post("/upload-optimized", response_model=ExtractedDataResponse)
async def upload_document_optimized(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None, description="Tipo de documento (factura, recibo, contrato, formulario)"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Sube documento y procesa con estrategia optimizada
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
        upload_dir.mkdir(exist_ok=True)
        
        # Guardar archivo
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro en base de datos
        db_document = Document(
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            mime_type=file.content_type
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Procesar documento
        try:
            # Para archivos pequeños, procesamiento síncrono
            if file_path.stat().st_size < 5 * 1024 * 1024:  # 5MB
                result = await processing_service._process_document_worker(str(file_path), document_type, db_document.id)
            else:
                # Para archivos grandes, procesamiento asíncrono
                job_id = await processing_service.process_document_async(str(file_path), document_type, db_document.id)
                result = await processing_service.get_job_status(job_id)
                
                if result.status.value == "failed":
                    raise HTTPException(status_code=500, detail=f"Error procesando documento: {result.error}")
                
                result = result.result
            
            # Actualizar documento con resultados si no se hizo en el worker
            if not result.get('metadata', {}).get('document_id'):
                db_document.raw_text = result['ocr']['text']
                db_document.extracted_data = result['extraction']
                db_document.confidence_score = int(result['extraction']['confidence'] * 100)
                db_document.ocr_provider = result['ocr']['provider']
                db_document.ocr_cost = str(result['ocr']['cost'])
                db_document.processing_time = str(result['ocr']['processing_time'])
                
                db.commit()
                db.refresh(db_document)
            
            return ExtractedDataResponse(
                document_id=db_document.id,
                filename=db_document.filename,
                extracted_data=result['extraction'],
                raw_text=result['ocr']['text'],
                confidence_score=db_document.confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error procesando documento {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error subiendo archivo {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")

@router.post("/upload-async")
async def upload_document_async(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None, description="Tipo de documento"),
    db: Session = Depends(get_db)
):
    """
    Sube documento y procesa de forma asíncrona
    """
    
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Crear directorio si no existe
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Guardar archivo
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro en base de datos
        db_document = Document(
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            mime_type=file.content_type
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Iniciar procesamiento asíncrono
        job_id = await processing_service.process_document_async(str(file_path), document_type, db_document.id)
        
        return {
            "message": "Documento subido y procesamiento iniciado",
            "document_id": db_document.id,
            "job_id": job_id,
            "status_url": f"/api/v1/jobs/{job_id}/status",
            "estimated_time": "2-5 minutos"
        }
        
    except Exception as e:
        logger.error(f"Error subiendo archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")

@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """
    Obtiene estado de trabajo de procesamiento
    """
    
    try:
        job_status = await processing_service.get_job_status(job_id)
        return job_status
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del trabajo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@router.get("/queue/stats")
async def get_queue_stats():
    """
    Obtiene estadísticas de la cola de procesamiento
    """
    
    try:
        stats = await processing_service.get_queue_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str):
    """
    Reintenta un trabajo fallido
    """
    
    try:
        success = await processing_service.retry_failed_job(job_id)
        if success:
            return {"message": "Trabajo reintentado exitosamente", "job_id": job_id}
        else:
            raise HTTPException(status_code=400, detail="No se pudo reintentar el trabajo")
        
    except Exception as e:
        logger.error(f"Error reintentando trabajo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reintentando trabajo: {str(e)}")

@router.post("/upload-batch")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    document_type: Optional[str] = Query(None, description="Tipo de documento para todos los archivos"),
    db: Session = Depends(get_db)
):
    """
    Sube múltiples documentos en lote
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # Usar el endpoint de upload asíncrono para cada archivo
            result = await upload_document_async(file, document_type, db)
            results.append(result)
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }
