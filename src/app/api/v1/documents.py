"""
Document Endpoints v1 (Legacy)
==============================

Endpoints legacy para compatibilidad.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from ...core.database import get_db
from ...repositories.document_repository import DocumentRepository
from ...schemas.document_consolidated import (
    DocumentResponseSchema,
    DocumentListResponseSchema
)
from pydantic import BaseModel
from typing import List as TypingList

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_documents(
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de documentos a retornar"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    status: Optional[str] = Query(None, description="Filtrar por estado de procesamiento"),
    search: Optional[str] = Query(None, description="Buscar en nombre de archivo o contenido"),
    db: Session = Depends(get_db)
):
    """Listar documentos con filtros opcionales"""
    try:
        repository = DocumentRepository(db)
        
        # Construir query base
        query = db.query(repository.model).filter(repository.model.is_deleted == False)
        
        # Aplicar filtros
        if document_type:
            query = query.filter(repository.model.document_type == document_type)
        if status:
            query = query.filter(repository.model.status == status)
        if search:
            search_filter = or_(
                repository.model.original_filename.ilike(f"%{search}%"),
                repository.model.filename.ilike(f"%{search}%"),
                repository.model.raw_text.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Obtener total antes de paginar
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        documents = query.order_by(repository.model.created_at.desc()).offset(skip).limit(limit).all()
        
        # Calcular paginación
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        has_next = skip + limit < total
        has_prev = skip > 0
        
        # Convertir a schemas
        document_schemas = []
        for doc in documents:
            try:
                # Generar UUID si no existe (para compatibilidad con schema)
                import uuid as uuid_lib
                doc_uuid = getattr(doc, 'uuid', None) or str(uuid_lib.uuid4())
                
                # Convertir status a enum válido
                status_map = {
                    "completed": "processed",
                    "pending": "uploaded",
                    "processing": "processing",
                    "failed": "failed"
                }
                doc_status = status_map.get(doc.status, "processed") if hasattr(doc, 'status') else "processed"
                
                # Función auxiliar para aplanar extracted_data de forma robusta
                def flatten_extracted_data(data):
                    """Aplana extracted_data asegurando que siempre tenga la estructura correcta"""
                    import json
                    
                    # Si es string, parsear
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except:
                            return {}
                    
                    # Si es None, retornar vacío
                    if data is None:
                        return {}
                    
                    # Si no es dict, retornar vacío
                    if not isinstance(data, dict):
                        return {}
                    
                    # Si ya está aplanado (tiene campos de factura directamente), retornar tal cual
                    if 'numero_factura' in data or 'emisor' in data or 'items' in data or 'totales' in data:
                        # Ya está aplanado, solo asegurar que tenga document_type
                        if 'document_type' not in data:
                            # Intentar detectar tipo
                            if 'numero_factura' in data:
                                data['document_type'] = 'factura'
                            elif 'numero_recibo' in data:
                                data['document_type'] = 'recibo'
                        return data
                    
                    # Si tiene structured_data anidado, aplanarlo
                    if 'structured_data' in data:
                        structured = data.get('structured_data', {})
                        if isinstance(structured, dict) and structured:
                            # Copiar structured_data como base
                            flattened = structured.copy()
                            
                            # Agregar metadata si existe
                            if 'document_type' in data:
                                flattened['document_type'] = data['document_type']
                            elif 'document_type' not in flattened:
                                # Detectar tipo
                                if 'numero_factura' in flattened:
                                    flattened['document_type'] = 'factura'
                                elif 'numero_recibo' in flattened:
                                    flattened['document_type'] = 'recibo'
                            
                            # Agregar confidence si existe
                            if 'confidence' in data:
                                flattened['confidence'] = data['confidence']
                            
                            # Agregar metadata si existe
                            if 'metadata' in data:
                                flattened['metadata'] = data['metadata']
                            
                            return flattened
                    
                    # Si tiene entities pero no structured_data, puede ser formato antiguo
                    if 'entities' in data and 'structured_data' not in data:
                        # Intentar construir desde entities
                        result = {}
                        if 'document_type' in data:
                            result['document_type'] = data['document_type']
                        if 'confidence' in data:
                            result['confidence'] = data['confidence']
                        # Agregar entities como metadata
                        if 'entities' in data:
                            result['entities'] = data['entities']
                        return result
                    
                    # Si no tiene estructura conocida, retornar tal cual (puede ser formato personalizado)
                    return data
                
                # Aplicar función de aplanado
                extracted_data = flatten_extracted_data(doc.extracted_data)
                
                # Logging para debugging (solo si está vacío o tiene problemas)
                if not extracted_data or (isinstance(extracted_data, dict) and len(extracted_data) == 0):
                    logger.warning(f"Documento {doc.id} tiene extracted_data vacío o inválido. Raw data: {doc.extracted_data}")
                
                # Extraer datos del documento
                doc_data = {
                    "id": doc.id,
                    "uuid": doc_uuid,
                    "filename": doc.original_filename or doc.filename,
                    "original_filename": doc.original_filename or doc.filename,
                    "file_path": doc.file_path,
                    "file_size": doc.file_size,
                    "mime_type": doc.mime_type,
                    "document_type": getattr(doc, 'document_type', None),
                    "status": doc_status,
                    "confidence_score": float(doc.confidence_score) / 100.0 if doc.confidence_score else None,
                    "raw_text": doc.raw_text[:200] if doc.raw_text else None,  # Primeros 200 caracteres para preview
                    "extracted_data": extracted_data,
                    "ocr_provider": getattr(doc, 'ocr_provider', None),
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "updated_at": doc.updated_at.isoformat() if hasattr(doc, 'updated_at') and doc.updated_at else None,
                    "is_deleted": getattr(doc, 'is_deleted', False)
                }
                # Calcular campos computados manualmente para evitar recursión
                if doc_data.get('file_size'):
                    doc_data['file_size_mb'] = round(doc_data['file_size'] / (1024 * 1024), 2)
                else:
                    doc_data['file_size_mb'] = None
                
                # Determinar si está procesado
                doc_data['is_processed'] = doc_status in ['processed', 'approved']
                
                # Determinar si necesita revisión
                doc_data['needs_review'] = (
                    doc_status == 'reviewing' or
                    (doc_data.get('confidence_score') is not None and doc_data['confidence_score'] < 0.7) or
                    doc_status == 'failed'
                )
                
                # Usar dict directamente para evitar problemas de recursión con el schema
                document_schemas.append(doc_data)
            except Exception as e:
                logger.warning(f"Error convirtiendo documento {doc.id}: {e}")
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")
                continue
        
        # Retornar respuesta simple sin usar el schema complejo para evitar recursión
        return {
            "documents": document_schemas,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando documentos: {str(e)}")

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un documento específico por ID"""
    try:
        repository = DocumentRepository(db)
        document = repository.get_by_id(document_id)
        
        if not document or document.is_deleted:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Generar UUID si no existe
        import uuid as uuid_lib
        doc_uuid = getattr(document, 'uuid', None) or str(uuid_lib.uuid4())
        
        # Convertir status a enum válido
        status_map = {
            "completed": "processed",
            "pending": "uploaded",
            "processing": "processing",
            "failed": "failed"
        }
        doc_status = status_map.get(document.status, "processed") if hasattr(document, 'status') else "processed"
        
        # Función auxiliar para aplanar extracted_data (misma que en list_documents)
        def flatten_extracted_data(data):
            """Aplana extracted_data asegurando que siempre tenga la estructura correcta"""
            import json
            
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    return {}
            
            if data is None:
                return {}
            
            if not isinstance(data, dict):
                return {}
            
            # Si ya está aplanado (tiene campos de factura directamente), retornar tal cual
            if 'numero_factura' in data or 'emisor' in data or 'items' in data or 'totales' in data:
                if 'document_type' not in data:
                    if 'numero_factura' in data:
                        data['document_type'] = 'factura'
                    elif 'numero_recibo' in data:
                        data['document_type'] = 'recibo'
                return data
            
            # Si tiene structured_data anidado, aplanarlo
            if 'structured_data' in data:
                structured = data.get('structured_data', {})
                if isinstance(structured, dict) and structured:
                    flattened = structured.copy()
                    if 'document_type' in data:
                        flattened['document_type'] = data['document_type']
                    elif 'document_type' not in flattened:
                        if 'numero_factura' in flattened:
                            flattened['document_type'] = 'factura'
                        elif 'numero_recibo' in flattened:
                            flattened['document_type'] = 'recibo'
                    if 'confidence' in data:
                        flattened['confidence'] = data['confidence']
                    if 'metadata' in data:
                        flattened['metadata'] = data['metadata']
                    return flattened
            
            # Si tiene entities pero no structured_data
            if 'entities' in data and 'structured_data' not in data:
                result = {}
                if 'document_type' in data:
                    result['document_type'] = data['document_type']
                if 'confidence' in data:
                    result['confidence'] = data['confidence']
                if 'entities' in data:
                    result['entities'] = data['entities']
                return result
            
            return data
        
        # Aplicar función de aplanado
        extracted_data = flatten_extracted_data(document.extracted_data)
        
        # Logging para debugging (solo si está vacío)
        if not extracted_data or (isinstance(extracted_data, dict) and len(extracted_data) == 0):
            logger.warning(f"Documento {document.id} tiene extracted_data vacío. Raw data: {document.extracted_data}")
        
        # Construir respuesta
        doc_data = {
            "id": document.id,
            "uuid": doc_uuid,
            "filename": document.original_filename or document.filename,
            "original_filename": document.original_filename or document.filename,
            "file_path": document.file_path,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "document_type": getattr(document, 'document_type', None),
            "status": doc_status,
            "confidence_score": float(document.confidence_score) / 100.0 if document.confidence_score else None,
            "raw_text": document.raw_text,
            "extracted_data": extracted_data,
            "ocr_provider": getattr(document, 'ocr_provider', None),
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if hasattr(document, 'updated_at') and document.updated_at else None,
            "is_deleted": getattr(document, 'is_deleted', False)
        }
        
        # Calcular campos computados
        if doc_data.get('file_size'):
            doc_data['file_size_mb'] = round(doc_data['file_size'] / (1024 * 1024), 2)
        else:
            doc_data['file_size_mb'] = None
        
        doc_data['is_processed'] = doc_status in ['processed', 'approved']
        doc_data['needs_review'] = (
            doc_status == 'reviewing' or
            (doc_data.get('confidence_score') is not None and doc_data['confidence_score'] < 0.7) or
            doc_status == 'failed'
        )
        
        return doc_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documento {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo documento: {str(e)}")

