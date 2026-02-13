"""
Rutas mejoradas para gestión de documentos
Utiliza schemas Pydantic mejorados con validaciones avanzadas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import csv
import json

# Importar schemas mejorados
from ..schemas.document_enhanced import (
    DocumentEnhancedCreate,
    DocumentEnhancedUpdate,
    DocumentEnhancedResponse,
    DocumentEnhancedListResponse,
    DocumentProcessingRequest,
    DocumentReviewRequest,
    DocumentSearchRequest,
    DocumentStatsResponse,
    DocumentBatchOperationRequest,
    DocumentExportRequest,
    DocumentTypeEnum,
    DocumentStatusEnum,
    OCRProviderEnum,
    ExtractionMethodEnum,
)

# Importar dependencias de autenticación (usar las existentes por ahora)
from ..auth.dependencies import get_current_user

# Importar servicios (crear compatibilidad con servicios existentes)
from ..services.document_service_enhanced import DocumentServiceEnhanced

router = APIRouter(prefix="/api/v2/documents", tags=["Documents Enhanced"])

# ============================================================================
# RUTAS DE CRUD BÁSICO
# ============================================================================

@router.post("/", response_model=DocumentEnhancedResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentEnhancedCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo documento con validaciones mejoradas
    
    - **filename**: Nombre del archivo (requerido)
    - **original_filename**: Nombre original del archivo (requerido)
    - **file_path**: Ruta del archivo (requerido)
    - **document_type**: Tipo de documento (opcional)
    - **priority**: Prioridad de procesamiento (1-10, por defecto 5)
    - **language**: Idioma del documento (por defecto 'es')
    - **organization_id**: ID de la organización (opcional)
    - **tags**: Lista de tags/etiquetas (opcional)
    """
    try:
        service = DocumentServiceEnhanced()
        document = await service.create_document(
            document_data=document_data,
            user_id=current_user.get("id")
        )
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear documento: {str(e)}"
        )

@router.get("/{document_id}", response_model=DocumentEnhancedResponse)
async def get_document(
    document_id: int = Path(..., description="ID del documento"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un documento por ID con información completa
    
    - **document_id**: ID único del documento
    - Retorna información completa incluyendo metadatos y campos calculados
    """
    try:
        service = DocumentServiceEnhanced()
        document = await service.get_document_by_id(
            document_id=document_id,
            user_id=current_user.get("id")
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener documento: {str(e)}"
        )

@router.put("/{document_id}", response_model=DocumentEnhancedResponse)
async def update_document(
    document_id: int = Path(..., description="ID del documento"),
    document_update: DocumentEnhancedUpdate = ...,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar un documento existente
    
    - **document_id**: ID del documento a actualizar
    - **document_update**: Datos a actualizar (solo campos enviados)
    """
    try:
        service = DocumentServiceEnhanced()
        document = await service.update_document(
            document_id=document_id,
            document_update=document_update,
            user_id=current_user.get("id")
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar documento: {str(e)}"
        )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int = Path(..., description="ID del documento"),
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar un documento (soft delete)
    
    - **document_id**: ID del documento a eliminar
    """
    try:
        service = DocumentServiceEnhanced()
        success = await service.delete_document(
            document_id=document_id,
            user_id=current_user.get("id")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar documento: {str(e)}"
        )

# ============================================================================
# RUTAS DE LISTADO Y BÚSQUEDA
# ============================================================================

@router.get("/", response_model=DocumentEnhancedListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    document_type: Optional[DocumentTypeEnum] = Query(None, description="Filtrar por tipo"),
    status: Optional[DocumentStatusEnum] = Query(None, description="Filtrar por estado"),
    ocr_provider: Optional[OCRProviderEnum] = Query(None, description="Filtrar por proveedor OCR"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Confianza mínima"),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Confianza máxima"),
    date_from: Optional[datetime] = Query(None, description="Fecha desde"),
    date_to: Optional[datetime] = Query(None, description="Fecha hasta"),
    tags: Optional[str] = Query(None, description="Tags separados por coma"),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|filename|confidence_score)$", description="Campo de ordenamiento"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar documentos con filtros avanzados
    
    - **page**: Número de página (por defecto 1)
    - **size**: Tamaño de página (por defecto 20, máximo 100)
    - **document_type**: Filtrar por tipo de documento
    - **status**: Filtrar por estado de procesamiento
    - **ocr_provider**: Filtrar por proveedor OCR usado
    - **min_confidence/max_confidence**: Filtrar por rango de confianza
    - **date_from/date_to**: Filtrar por rango de fechas
    - **tags**: Tags separados por coma
    - **sort_by**: Campo de ordenamiento
    - **sort_order**: Orden (asc/desc)
    """
    try:
        # Convertir tags string a lista
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
        
        search_request = DocumentSearchRequest(
            document_type=document_type,
            status=status,
            ocr_provider=ocr_provider,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            date_from=date_from,
            date_to=date_to,
            tags=tags_list,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        service = DocumentServiceEnhanced()
        result = await service.search_documents(
            search_request=search_request,
            user_id=current_user.get("id")
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en búsqueda de documentos: {str(e)}"
        )

@router.post("/search", response_model=DocumentEnhancedListResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Búsqueda avanzada de documentos con texto libre
    
    - **query**: Texto de búsqueda libre
    - **filters**: Filtros adicionales
    - **pagination**: Configuración de paginación
    - **sorting**: Configuración de ordenamiento
    """
    try:
        service = DocumentServiceEnhanced()
        result = await service.search_documents(
            search_request=search_request,
            user_id=current_user.get("id")
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en búsqueda avanzada: {str(e)}"
        )

# ============================================================================
# RUTAS DE PROCESAMIENTO
# ============================================================================

@router.post("/{document_id}/process", response_model=Dict[str, Any])
async def process_document(
    document_id: int = Path(..., description="ID del documento"),
    processing_request: DocumentProcessingRequest = ...,
    current_user: dict = Depends(get_current_user)
):
    """
    Procesar un documento (OCR + Extracción)
    
    - **document_id**: ID del documento a procesar
    - **ocr_provider**: Proveedor OCR a usar (opcional)
    - **extraction_method**: Método de extracción (opcional)
    - **force_reprocess**: Forzar reprocesamiento (por defecto False)
    - **priority**: Prioridad del procesamiento (1-10)
    """
    try:
        service = DocumentServiceEnhanced()
        result = await service.process_document(
            document_id=document_id,
            processing_request=processing_request,
            user_id=current_user.get("id")
        )
        
        return {
            "message": "Documento enviado a procesamiento",
            "job_id": result.get("job_id"),
            "status_url": f"/api/v2/jobs/{result.get('job_id')}/status",
            "estimated_time": result.get("estimated_time", "2-5 minutos")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar documento: {str(e)}"
        )

@router.post("/{document_id}/review", response_model=Dict[str, Any])
async def review_document(
    document_id: int = Path(..., description="ID del documento"),
    review_request: DocumentReviewRequest = ...,
    current_user: dict = Depends(get_current_user)
):
    """
    Revisar un documento (aprobar/rechazar)
    
    - **document_id**: ID del documento a revisar
    - **action**: Acción a realizar (approve/reject/request_changes)
    - **review_notes**: Notas de la revisión (opcional)
    - **confidence_override**: Sobrescribir confianza (opcional)
    """
    try:
        service = DocumentServiceEnhanced()
        result = await service.review_document(
            document_id=document_id,
            review_request=review_request,
            user_id=current_user.get("id")
        )
        
        return {
            "message": f"Documento {review_request.action} exitosamente",
            "document_id": document_id,
            "review_notes": review_request.review_notes
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al revisar documento: {str(e)}"
        )

# ============================================================================
# RUTAS DE OPERACIONES EN LOTE
# ============================================================================

@router.post("/batch", response_model=Dict[str, Any])
async def batch_operation(
    batch_request: DocumentBatchOperationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Operaciones en lote sobre múltiples documentos
    
    - **document_ids**: Lista de IDs de documentos (máximo 100)
    - **operation**: Operación a realizar (delete/update_status/update_type/add_tags/remove_tags)
    - **parameters**: Parámetros adicionales según la operación
    """
    try:
        service = DocumentServiceEnhanced()
        result = await service.batch_operation(
            batch_request=batch_request,
            user_id=current_user.get("id")
        )
        
        return {
            "message": f"Operación {batch_request.operation} completada",
            "processed": result.get("processed", 0),
            "errors": result.get("errors", 0),
            "details": result.get("details", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en operación en lote: {str(e)}"
        )

# ============================================================================
# RUTAS DE EXPORTACIÓN
# ============================================================================

@router.post("/export")
async def export_documents(
    export_request: DocumentExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Exportar documentos en diferentes formatos
    
    - **document_ids**: IDs específicos (opcional)
    - **filters**: Filtros de búsqueda (opcional)
    - **format**: Formato de exportación (json/csv/xlsx/pdf)
    - **include_extracted_data**: Incluir datos extraídos
    - **include_raw_text**: Incluir texto crudo
    """
    try:
        service = DocumentServiceEnhanced()
        
        if export_request.format == "json":
            # Exportar como JSON
            data = await service.export_documents_json(
                export_request=export_request,
                user_id=current_user.get("id")
            )
            return data
            
        elif export_request.format == "csv":
            # Exportar como CSV
            csv_data = await service.export_documents_csv(
                export_request=export_request,
                user_id=current_user.get("id")
            )
            
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
            
        elif export_request.format == "xlsx":
            # Exportar como Excel
            excel_data = await service.export_documents_xlsx(
                export_request=export_request,
                user_id=current_user.get("id")
            )
            
            return StreamingResponse(
                io.BytesIO(excel_data),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de exportación no soportado: {export_request.format}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al exportar documentos: {str(e)}"
        )

# ============================================================================
# RUTAS DE ESTADÍSTICAS
# ============================================================================

@router.get("/stats/overview", response_model=DocumentStatsResponse)
async def get_document_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener estadísticas generales de documentos
    
    Retorna estadísticas agregadas incluyendo:
    - Total de documentos
    - Distribución por estado, tipo, proveedor OCR
    - Estadísticas mensuales
    - Promedio de confianza
    - Tiempo total de procesamiento
    - Almacenamiento total
    """
    try:
        service = DocumentServiceEnhanced()
        stats = await service.get_document_stats(
            user_id=current_user.get("id")
        )
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

# ============================================================================
# RUTAS DE SUBIDA DE ARCHIVOS
# ============================================================================

@router.post("/upload", response_model=DocumentEnhancedResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Archivo a subir"),
    document_type: Optional[DocumentTypeEnum] = Query(None, description="Tipo de documento"),
    priority: int = Query(5, ge=1, le=10, description="Prioridad de procesamiento"),
    language: str = Query("es", description="Idioma del documento"),
    tags: Optional[str] = Query(None, description="Tags separados por coma"),
    auto_process: bool = Query(True, description="Procesar automáticamente"),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir un nuevo documento
    
    - **file**: Archivo a subir (PDF, JPG, PNG, etc.)
    - **document_type**: Tipo de documento (opcional)
    - **priority**: Prioridad de procesamiento (1-10)
    - **language**: Idioma del documento
    - **tags**: Tags separados por coma
    - **auto_process**: Procesar automáticamente después de subir
    """
    try:
        # Validar tipo de archivo
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
            "image/bmp"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no soportado: {file.content_type}"
            )
        
        # Validar tamaño de archivo (máximo 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo es demasiado grande. Máximo 50MB"
            )
        
        # Convertir tags string a lista
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
        
        service = DocumentServiceEnhanced()
        document = await service.upload_document(
            file=file,
            document_type=document_type,
            priority=priority,
            language=language,
            tags=tags_list,
            auto_process=auto_process,
            user_id=current_user.get("id")
        )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al subir documento: {str(e)}"
        )