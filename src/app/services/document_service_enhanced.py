"""
Servicio mejorado para gestión de documentos
Utiliza schemas Pydantic mejorados y compatibilidad con servicios legacy
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import csv
import io
from sqlalchemy.orm import Session

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
    DocumentLegacyToEnhanced,
    DocumentEnhancedToLegacy,
    DocumentTypeEnum,
    DocumentStatusEnum,
    OCRProviderEnum,
    ExtractionMethodEnum,
)

# Importar modelos mejorados
from ..models.document_enhanced import Document as DocumentEnhanced
from ..models.document import Document as DocumentLegacy

# Importar servicios existentes para compatibilidad
from .document_service import DocumentService
from .intelligent_extraction_service import IntelligentExtractionService
from .async_processing_service import AsyncProcessingService

# Importar dependencias
from ..core.database import get_db
from ..core.config import settings

class DocumentServiceEnhanced:
    """Servicio mejorado para gestión de documentos con compatibilidad legacy"""
    
    def __init__(self):
        self.legacy_service = DocumentService()
        self.extraction_service = IntelligentExtractionService()
        self.processing_service = AsyncProcessingService()
    
    # ============================================================================
    # MÉTODOS DE CRUD BÁSICO
    # ============================================================================
    
    async def create_document(
        self, 
        document_data: DocumentEnhancedCreate, 
        user_id: Optional[int] = None
    ) -> DocumentEnhancedResponse:
        """Crear un nuevo documento mejorado"""
        try:
            # Por ahora, crear usando el servicio legacy y convertir
            legacy_data = {
                "filename": document_data.filename,
                "original_filename": document_data.original_filename,
                "file_path": document_data.file_path,
                "file_size": document_data.file_size,
                "mime_type": document_data.mime_type,
            }
            
            # Crear documento legacy
            legacy_document = await self.legacy_service.create_document(legacy_data)
            
            # Convertir a formato mejorado
            enhanced_document = await self._convert_legacy_to_enhanced(
                legacy_document, 
                user_id=user_id,
                organization_id=document_data.organization_id,
                document_type=document_data.document_type,
                priority=document_data.priority,
                language=document_data.language,
                tags=document_data.tags
            )
            
            return enhanced_document
            
        except Exception as e:
            raise Exception(f"Error al crear documento: {str(e)}")
    
    async def get_document_by_id(
        self, 
        document_id: int, 
        user_id: Optional[int] = None
    ) -> Optional[DocumentEnhancedResponse]:
        """Obtener documento por ID"""
        try:
            # Intentar obtener documento mejorado primero
            enhanced_doc = await self._get_enhanced_document(document_id)
            if enhanced_doc:
                return self._convert_enhanced_to_response(enhanced_doc)
            
            # Si no existe, obtener documento legacy
            legacy_doc = await self.legacy_service.get_document_by_id(document_id)
            if legacy_doc:
                return await self._convert_legacy_to_enhanced_response(legacy_doc)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error al obtener documento: {str(e)}")
    
    async def update_document(
        self, 
        document_id: int, 
        document_update: DocumentEnhancedUpdate,
        user_id: Optional[int] = None
    ) -> Optional[DocumentEnhancedResponse]:
        """Actualizar documento"""
        try:
            # Intentar actualizar documento mejorado primero
            enhanced_doc = await self._get_enhanced_document(document_id)
            if enhanced_doc:
                return await self._update_enhanced_document(enhanced_doc, document_update)
            
            # Si no existe, actualizar documento legacy
            legacy_doc = await self.legacy_service.get_document_by_id(document_id)
            if legacy_doc:
                # Convertir update a formato legacy
                legacy_update = self._convert_enhanced_update_to_legacy(document_update)
                updated_legacy = await self.legacy_service.update_document(document_id, legacy_update)
                
                if updated_legacy:
                    return await self._convert_legacy_to_enhanced_response(updated_legacy)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error al actualizar documento: {str(e)}")
    
    async def delete_document(
        self, 
        document_id: int, 
        user_id: Optional[int] = None
    ) -> bool:
        """Eliminar documento (soft delete)"""
        try:
            # Intentar eliminar documento mejorado primero
            enhanced_doc = await self._get_enhanced_document(document_id)
            if enhanced_doc:
                return await self._delete_enhanced_document(enhanced_doc)
            
            # Si no existe, eliminar documento legacy
            return await self.legacy_service.delete_document(document_id)
            
        except Exception as e:
            raise Exception(f"Error al eliminar documento: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE BÚSQUEDA Y LISTADO
    # ============================================================================
    
    async def search_documents(
        self, 
        search_request: DocumentSearchRequest,
        user_id: Optional[int] = None
    ) -> DocumentEnhancedListResponse:
        """Búsqueda avanzada de documentos"""
        try:
            # Por ahora, usar servicio legacy con filtros básicos
            # TODO: Implementar búsqueda mejorada con full-text search
            
            filters = {}
            if search_request.document_type:
                filters["document_type"] = search_request.document_type.value
            if search_request.status:
                filters["status"] = search_request.status.value
            if search_request.min_confidence:
                filters["min_confidence"] = search_request.min_confidence
            if search_request.max_confidence:
                filters["max_confidence"] = search_request.max_confidence
            if search_request.date_from:
                filters["date_from"] = search_request.date_from
            if search_request.date_to:
                filters["date_to"] = search_request.date_to
            
            # Obtener documentos legacy
            legacy_result = await self.legacy_service.get_documents(
                page=search_request.page,
                size=search_request.size,
                **filters
            )
            
            # Convertir a formato mejorado
            enhanced_documents = []
            for legacy_doc in legacy_result.get("documents", []):
                enhanced_doc = await self._convert_legacy_to_enhanced_response(legacy_doc)
                enhanced_documents.append(enhanced_doc)
            
            return DocumentEnhancedListResponse(
                documents=enhanced_documents,
                total=legacy_result.get("total", 0),
                page=search_request.page,
                size=search_request.size,
                total_pages=(legacy_result.get("total", 0) + search_request.size - 1) // search_request.size,
                has_next=search_request.page < (legacy_result.get("total", 0) + search_request.size - 1) // search_request.size,
                has_prev=search_request.page > 1
            )
            
        except Exception as e:
            raise Exception(f"Error en búsqueda de documentos: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE PROCESAMIENTO
    # ============================================================================
    
    async def process_document(
        self, 
        document_id: int, 
        processing_request: DocumentProcessingRequest,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Procesar documento con configuración avanzada"""
        try:
            # Obtener documento
            document = await self.get_document_by_id(document_id, user_id)
            if not document:
                raise Exception("Documento no encontrado")
            
            # Configurar procesamiento
            processing_config = {
                "ocr_provider": processing_request.ocr_provider.value if processing_request.ocr_provider else None,
                "extraction_method": processing_request.extraction_method.value if processing_request.extraction_method else None,
                "force_reprocess": processing_request.force_reprocess,
                "priority": processing_request.priority
            }
            
            # Enviar a procesamiento asíncrono
            job_result = await self.processing_service.process_document_async(
                document_id=document_id,
                config=processing_config
            )
            
            return {
                "job_id": job_result.get("job_id"),
                "estimated_time": job_result.get("estimated_time", "2-5 minutos"),
                "status": "queued"
            }
            
        except Exception as e:
            raise Exception(f"Error al procesar documento: {str(e)}")
    
    async def review_document(
        self, 
        document_id: int, 
        review_request: DocumentReviewRequest,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Revisar documento (aprobar/rechazar)"""
        try:
            # Obtener documento
            document = await self.get_document_by_id(document_id, user_id)
            if not document:
                raise Exception("Documento no encontrado")
            
            # Preparar actualización
            update_data = DocumentEnhancedUpdate(
                status=DocumentStatusEnum.APPROVED if review_request.action == "approve" else DocumentStatusEnum.REJECTED,
                review_notes=review_request.review_notes
            )
            
            if review_request.confidence_override:
                update_data.confidence_score = review_request.confidence_override
            
            # Actualizar documento
            await self.update_document(document_id, update_data, user_id)
            
            return {
                "message": f"Documento {review_request.action} exitosamente",
                "document_id": document_id
            }
            
        except Exception as e:
            raise Exception(f"Error al revisar documento: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE OPERACIONES EN LOTE
    # ============================================================================
    
    async def batch_operation(
        self, 
        batch_request: DocumentBatchOperationRequest,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Operaciones en lote sobre documentos"""
        try:
            processed = 0
            errors = 0
            details = []
            
            for document_id in batch_request.document_ids:
                try:
                    if batch_request.operation == "delete":
                        success = await self.delete_document(document_id, user_id)
                        if success:
                            processed += 1
                        else:
                            errors += 1
                            details.append({"document_id": document_id, "error": "No encontrado"})
                    
                    elif batch_request.operation == "update_status":
                        new_status = batch_request.parameters.get("status")
                        if new_status:
                            update_data = DocumentEnhancedUpdate(status=DocumentStatusEnum(new_status))
                            result = await self.update_document(document_id, update_data, user_id)
                            if result:
                                processed += 1
                            else:
                                errors += 1
                                details.append({"document_id": document_id, "error": "No encontrado"})
                    
                    # TODO: Implementar otras operaciones (update_type, add_tags, remove_tags)
                    
                except Exception as e:
                    errors += 1
                    details.append({"document_id": document_id, "error": str(e)})
            
            return {
                "processed": processed,
                "errors": errors,
                "details": details
            }
            
        except Exception as e:
            raise Exception(f"Error en operación en lote: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE EXPORTACIÓN
    # ============================================================================
    
    async def export_documents_json(
        self, 
        export_request: DocumentExportRequest,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Exportar documentos como JSON"""
        try:
            # Obtener documentos
            if export_request.document_ids:
                documents = []
                for doc_id in export_request.document_ids:
                    doc = await self.get_document_by_id(doc_id, user_id)
                    if doc:
                        documents.append(doc.dict())
            else:
                # Usar filtros
                search_request = DocumentSearchRequest(
                    page=1,
                    size=1000,  # Máximo para exportación
                    **export_request.filters.dict() if export_request.filters else {}
                )
                result = await self.search_documents(search_request, user_id)
                documents = [doc.dict() for doc in result.documents]
            
            return {
                "exported_at": datetime.now().isoformat(),
                "total_documents": len(documents),
                "format": "json",
                "documents": documents
            }
            
        except Exception as e:
            raise Exception(f"Error al exportar documentos JSON: {str(e)}")
    
    async def export_documents_csv(
        self, 
        export_request: DocumentExportRequest,
        user_id: Optional[int] = None
    ) -> str:
        """Exportar documentos como CSV"""
        try:
            # Obtener documentos JSON
            json_data = await self.export_documents_json(export_request, user_id)
            documents = json_data["documents"]
            
            if not documents:
                return ""
            
            # Crear CSV
            output = io.StringIO()
            fieldnames = [
                "id", "filename", "original_filename", "document_type", "status",
                "confidence_score", "created_at", "updated_at"
            ]
            
            if export_request.include_extracted_data:
                fieldnames.extend(["extracted_data"])
            
            if export_request.include_raw_text:
                fieldnames.extend(["raw_text"])
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for doc in documents:
                row = {
                    "id": doc.get("id"),
                    "filename": doc.get("filename"),
                    "original_filename": doc.get("original_filename"),
                    "document_type": doc.get("document_type"),
                    "status": doc.get("status"),
                    "confidence_score": doc.get("confidence_score"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at")
                }
                
                if export_request.include_extracted_data and doc.get("extracted_data"):
                    row["extracted_data"] = json.dumps(doc["extracted_data"], ensure_ascii=False)
                
                if export_request.include_raw_text:
                    row["raw_text"] = doc.get("raw_text", "")
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Error al exportar documentos CSV: {str(e)}")
    
    async def export_documents_xlsx(
        self, 
        export_request: DocumentExportRequest,
        user_id: Optional[int] = None
    ) -> bytes:
        """Exportar documentos como Excel"""
        try:
            # Por ahora, usar CSV como base y convertir
            csv_data = await self.export_documents_csv(export_request, user_id)
            
            # TODO: Implementar conversión real a Excel usando openpyxl
            # Por ahora, retornar CSV como bytes
            return csv_data.encode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error al exportar documentos Excel: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS
    # ============================================================================
    
    async def get_document_stats(
        self, 
        user_id: Optional[int] = None
    ) -> DocumentStatsResponse:
        """Obtener estadísticas de documentos"""
        try:
            # TODO: Implementar estadísticas reales
            # Por ahora, retornar datos de ejemplo
            
            return DocumentStatsResponse(
                total_documents=0,
                by_status={"processed": 0, "pending": 0, "failed": 0},
                by_type={"factura": 0, "recibo": 0, "otro": 0},
                by_ocr_provider={"tesseract": 0, "google_vision": 0},
                by_month={},
                average_confidence=0.0,
                total_processing_time=0.0,
                total_storage_mb=0.0
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener estadísticas: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE SUBIDA DE ARCHIVOS
    # ============================================================================
    
    async def upload_document(
        self,
        file,
        document_type: Optional[DocumentTypeEnum] = None,
        priority: int = 5,
        language: str = "es",
        tags: Optional[List[str]] = None,
        auto_process: bool = True,
        user_id: Optional[int] = None
    ) -> DocumentEnhancedResponse:
        """Subir y procesar documento"""
        try:
            # Guardar archivo usando servicio legacy
            legacy_doc = await self.legacy_service.upload_and_process_file(
                file=file,
                auto_process=auto_process
            )
            
            # Convertir a formato mejorado
            enhanced_doc = await self._convert_legacy_to_enhanced(
                legacy_doc,
                user_id=user_id,
                document_type=document_type,
                priority=priority,
                language=language,
                tags=tags or []
            )
            
            return enhanced_doc
            
        except Exception as e:
            raise Exception(f"Error al subir documento: {str(e)}")
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CONVERSIÓN
    # ============================================================================
    
    async def _convert_legacy_to_enhanced(
        self, 
        legacy_doc: dict,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        document_type: Optional[DocumentTypeEnum] = None,
        priority: int = 5,
        language: str = "es",
        tags: Optional[List[str]] = None
    ) -> DocumentEnhancedResponse:
        """Convertir documento legacy a formato mejorado"""
        try:
            return DocumentEnhancedResponse(
                id=legacy_doc.get("id"),
                uuid=f"legacy_{legacy_doc.get('id')}",  # Generar UUID para documentos legacy
                filename=legacy_doc.get("filename"),
                original_filename=legacy_doc.get("original_filename"),
                file_path=legacy_doc.get("file_path"),
                file_size=legacy_doc.get("file_size"),
                mime_type=legacy_doc.get("mime_type"),
                document_type=document_type,
                status=DocumentStatusEnum.PROCESSED if legacy_doc.get("raw_text") else DocumentStatusEnum.UPLOADED,
                priority=priority,
                raw_text=legacy_doc.get("raw_text"),
                extracted_data=legacy_doc.get("extracted_data"),
                confidence_score=legacy_doc.get("confidence_score"),
                quality_score=None,
                ocr_provider=OCRProviderEnum.TESSERACT if legacy_doc.get("ocr_provider") == "tesseract" else None,
                extraction_method=None,
                ocr_cost=0.0,
                processing_time_seconds=legacy_doc.get("processing_time"),
                language=language,
                page_count=None,
                word_count=None,
                user_id=user_id,
                organization_id=organization_id,
                reviewed_by=None,
                review_notes=None,
                created_at=datetime.fromisoformat(legacy_doc.get("created_at").replace('Z', '+00:00')) if legacy_doc.get("created_at") else datetime.now(),
                updated_at=datetime.fromisoformat(legacy_doc.get("updated_at").replace('Z', '+00:00')) if legacy_doc.get("updated_at") else None,
                processed_at=datetime.fromisoformat(legacy_doc.get("updated_at").replace('Z', '+00:00')) if legacy_doc.get("raw_text") and legacy_doc.get("updated_at") else None,
                reviewed_at=None,
                is_deleted=False,
                deleted_at=None,
                file_size_mb=legacy_doc.get("file_size", 0) / (1024 * 1024) if legacy_doc.get("file_size") else 0,
                is_processed=bool(legacy_doc.get("raw_text")),
                needs_review=legacy_doc.get("confidence_score", 0) < 0.8 if legacy_doc.get("confidence_score") else False
            )
            
        except Exception as e:
            raise Exception(f"Error al convertir documento legacy: {str(e)}")
    
    async def _convert_legacy_to_enhanced_response(
        self, 
        legacy_doc: dict
    ) -> DocumentEnhancedResponse:
        """Convertir documento legacy a respuesta mejorada"""
        return await self._convert_legacy_to_enhanced(legacy_doc)
    
    def _convert_enhanced_update_to_legacy(
        self, 
        enhanced_update: DocumentEnhancedUpdate
    ) -> dict:
        """Convertir actualización mejorada a formato legacy"""
        legacy_update = {}
        
        if enhanced_update.raw_text is not None:
            legacy_update["raw_text"] = enhanced_update.raw_text
        if enhanced_update.extracted_data is not None:
            legacy_update["extracted_data"] = enhanced_update.extracted_data
        if enhanced_update.confidence_score is not None:
            legacy_update["confidence_score"] = enhanced_update.confidence_score
        if enhanced_update.ocr_provider is not None:
            legacy_update["ocr_provider"] = enhanced_update.ocr_provider.value
        if enhanced_update.processing_time_seconds is not None:
            legacy_update["processing_time"] = enhanced_update.processing_time_seconds
        
        return legacy_update
    
    # ============================================================================
    # MÉTODOS PRIVADOS PARA MODELOS MEJORADOS
    # ============================================================================
    
    async def _get_enhanced_document(self, document_id: int):
        """Obtener documento del modelo mejorado"""
        # TODO: Implementar cuando esté disponible el modelo mejorado
        return None
    
    async def _update_enhanced_document(self, enhanced_doc, document_update: DocumentEnhancedUpdate):
        """Actualizar documento del modelo mejorado"""
        # TODO: Implementar cuando esté disponible el modelo mejorado
        return None
    
    async def _delete_enhanced_document(self, enhanced_doc):
        """Eliminar documento del modelo mejorado"""
        # TODO: Implementar cuando esté disponible el modelo mejorado
        return True
    
    def _convert_enhanced_to_response(self, enhanced_doc):
        """Convertir documento mejorado a respuesta"""
        # TODO: Implementar cuando esté disponible el modelo mejorado
        return None