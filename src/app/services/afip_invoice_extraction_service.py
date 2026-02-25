"""
Servicio especializado para extracción de datos de facturas AFIP/ARCA.

Orquesta extracción desde texto (AfipTextExtractor), OCR especializado opcional
y validación AFIP. Los patrones, validadores y la lógica de extracción de texto
están en el paquete afip/ para mantener este archivo manejable.
"""
import logging
from typing import Dict, Any, Optional

from PIL import Image

from .afip import AFIPInvoiceData
from .afip.afip_text_extractor import AfipTextExtractor
from .afip.afip_validators import validate_cuit, validate_currency

logger = logging.getLogger(__name__)


class AFIPInvoiceExtractionService:
    """
    Servicio para extraer datos de facturas AFIP/ARCA desde texto e imagen.
    """

    def __init__(
        self,
        validation_service=None,
        specialized_ocr=None,
        universal_validation=None,
    ):
        if validation_service is None:
            from .afip_validation_service import AFIPValidationService
            validation_service = AFIPValidationService()
        if specialized_ocr is None:
            from .specialized_ocr_service import SpecializedOCRService
            specialized_ocr = SpecializedOCRService()
        if universal_validation is None:
            from .universal_validation_service import UniversalValidationService
            universal_validation = UniversalValidationService()

        self.validation_service = validation_service
        self.specialized_ocr = specialized_ocr
        self.universal_validation = universal_validation
        self._text_extractor = AfipTextExtractor()

    def extract_afip_invoice_data(
        self, text: str, image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrae datos de factura AFIP desde texto y opcionalmente mejora con OCR sobre la imagen.
        """
        try:
            logger.info("Iniciando extracción de datos AFIP")
            invoice_data = AFIPInvoiceData()
            self._text_extractor.extract_all(text, invoice_data)

            if image_path:
                self._enhance_with_specialized_ocr(image_path, invoice_data)

            result = self._to_dict(invoice_data)
            logger.info(
                f"Datos AFIP extraídos: {invoice_data.campos_extraidos} campos, "
                f"{len(invoice_data.campos_faltantes)} faltantes"
            )
            return result
        except Exception as e:
            logger.error(f"Error extrayendo datos AFIP: {e}")
            return {}

    def _enhance_with_specialized_ocr(
        self, image_path: str, invoice_data: AFIPInvoiceData
    ) -> None:
        """Mejora la extracción con OCR especializado para campos críticos."""
        try:
            logger.info("Aplicando OCR especializado para campos críticos")
            if not invoice_data.cae_numero:
                cae_result = self.specialized_ocr.extract_cae_from_invoice(image_path)
                if cae_result.get("cae_number") and cae_result.get("confidence", 0) > 0.5:
                    invoice_data.cae_numero = cae_result["cae_number"]

            if not invoice_data.cuit_emisor:
                cuit_emisor = self._extract_cuit_specialized(image_path, "emisor")
                if cuit_emisor:
                    invoice_data.cuit_emisor = cuit_emisor
            if not invoice_data.cuit_comprador:
                cuit_comprador = self._extract_cuit_specialized(image_path, "comprador")
                if cuit_comprador:
                    invoice_data.cuit_comprador = cuit_comprador
            if not invoice_data.importe_total:
                importe_total = self._extract_amount_specialized(image_path)
                if importe_total:
                    invoice_data.importe_total = importe_total
        except Exception as e:
            logger.error(f"Error en OCR especializado: {e}")

    def _extract_cuit_specialized(self, image_path: str, position: str) -> Optional[str]:
        try:
            image = Image.open(image_path)
            width, height = image.size
            if position == "emisor":
                regions = [
                    (0, height // 4, width // 2, height // 2),
                    (0, height // 3, width // 2, height // 3),
                ]
            else:
                regions = [
                    (width // 2, height // 4, width // 2, height // 2),
                    (width // 2, height // 3, width // 2, height // 3),
                ]
            for x, y, w, h in regions:
                cropped = image.crop((x, y, x + w, y + h))
                text = self.specialized_ocr.extract_small_field_from_image(cropped, "cuit")
                if text and validate_cuit(text):
                    return text
        except Exception as e:
            logger.error(f"Error extrayendo CUIT {position}: {e}")
        return None

    def _extract_amount_specialized(self, image_path: str) -> Optional[str]:
        try:
            image = Image.open(image_path)
            width, height = image.size
            regions = [
                (width // 2, height * 3 // 4, width // 2, height // 4),
                (width * 2 // 3, height * 2 // 3, width // 3, height // 3),
            ]
            for x, y, w, h in regions:
                cropped = image.crop((x, y, x + w, y + h))
                text = self.specialized_ocr.extract_small_field_from_image(cropped, "amount")
                if text and validate_currency(text):
                    return text
        except Exception as e:
            logger.error(f"Error extrayendo importe total: {e}")
        return None

    def _to_dict(self, invoice_data: AFIPInvoiceData) -> Dict[str, Any]:
        """Convierte AFIPInvoiceData a diccionario y agrega validación AFIP si aplica."""
        result = {
            "tipo_documento": "factura_afip",
            "informacion_comprobante": {
                "tipo": invoice_data.tipo_comprobante,
                "punto_venta": invoice_data.punto_venta,
                "numero": invoice_data.numero_comprobante,
                "fecha_emision": invoice_data.fecha_emision,
                "fecha_vencimiento": invoice_data.fecha_vencimiento,
            },
            "emisor": {
                "razon_social": invoice_data.razon_social_emisor,
                "nombre_fantasia": invoice_data.nombre_fantasia,
                "domicilio": invoice_data.domicilio_comercial,
                "codigo_postal": invoice_data.codigo_postal,
                "localidad": invoice_data.localidad,
                "provincia": invoice_data.provincia,
                "cuit": invoice_data.cuit_emisor,
                "condicion_iva": invoice_data.condicion_iva_emisor,
                "numero_ingresos_brutos": invoice_data.numero_ingresos_brutos,
                "periodo_desde": invoice_data.periodo_facturado_desde,
                "periodo_hasta": invoice_data.periodo_facturado_hasta,
            },
            "comprador": {
                "cuit": invoice_data.cuit_comprador,
                "razon_social": invoice_data.razon_social_comprador,
                "domicilio": invoice_data.domicilio_comprador,
                "condicion_iva": invoice_data.condicion_iva_comprador,
                "condicion_venta": invoice_data.condicion_venta,
                "ingresos_brutos": invoice_data.ingresos_brutos,
                "fecha_inicio_actividades": invoice_data.fecha_inicio_actividades,
            },
            "productos": invoice_data.productos,
            "iva": {
                "importe_total": invoice_data.importe_iva,
                "importe_21": invoice_data.importe_iva_21,
                "importe_10_5": invoice_data.importe_iva_10_5,
                "importe_27": invoice_data.importe_iva_27,
                "importe_0": invoice_data.importe_iva_0,
                "alicuotas": invoice_data.alicuotas_iva,
            },
            "impuestos_tributos": {
                "otros_tributos": invoice_data.importe_otros_tributos,
                "detalle_otros_tributos": invoice_data.detalle_otros_tributos,
                "impuestos_internos": invoice_data.importe_impuestos_internos,
                "percepciones_iva": invoice_data.importe_percepciones_iva,
                "percepciones_iibb": invoice_data.importe_percepciones_iibb,
                "percepciones_municipales": invoice_data.importe_percepciones_municipales,
            },
            "totales": {
                "subtotal": invoice_data.subtotal,
                "subtotal_neto": invoice_data.subtotal_neto,
                "importe_exento": invoice_data.importe_exento,
                "importe_no_gravado": invoice_data.importe_no_gravado,
                "otros_tributos": invoice_data.importe_otros_tributos,
                "total": invoice_data.importe_total,
            },
            "afip": {
                "cae_numero": invoice_data.cae_numero,
                "cae_vencimiento": invoice_data.fecha_vencimiento_cae,
                "pagina_actual": invoice_data.pagina_actual,
                "total_paginas": invoice_data.total_paginas,
                "codigo_qr": invoice_data.codigo_qr,
            },
            "informacion_adicional": {
                "numero_remito": invoice_data.numero_remito,
                "forma_pago": invoice_data.forma_pago,
                "observaciones": invoice_data.observaciones,
                "punto_entrega": invoice_data.punto_entrega,
                "informacion_transporte": invoice_data.informacion_transporte,
            },
            "retenciones": {
                "importe_retenciones_iva": invoice_data.importe_retenciones_iva,
                "importe_retenciones_iibb": invoice_data.importe_retenciones_iibb,
                "importe_retenciones_ganancias": invoice_data.importe_retenciones_ganancias,
                "importe_retenciones_suss": invoice_data.importe_retenciones_suss,
                "detalle": invoice_data.retenciones,
            },
            "percepciones_detalladas": {
                "detalle_iva": invoice_data.detalle_percepciones_iva,
                "detalle_iibb": invoice_data.detalle_percepciones_iibb,
                "detalle_municipales": invoice_data.detalle_percepciones_municipales,
            },
            "pagos": {
                "importe_pagado": invoice_data.importe_pagado,
                "importe_pendiente": invoice_data.importe_pendiente,
                "fecha_ultimo_pago": invoice_data.fecha_ultimo_pago,
                "metodo_pago": invoice_data.metodo_pago,
                "numero_cheque": invoice_data.numero_cheque,
                "banco_cheque": invoice_data.banco_cheque,
                "numero_transferencia": invoice_data.numero_transferencia,
                "detalle": invoice_data.pagos,
            },
            "comprobantes_relacionados": {
                "nota_credito": invoice_data.nota_credito_relacionada,
                "nota_debito": invoice_data.nota_debito_relacionada,
                "factura_original": invoice_data.factura_original,
                "detalle": invoice_data.comprobantes_relacionados,
            },
            "exportacion": {
                "es_exportacion": invoice_data.es_exportacion,
                "codigo_destino": invoice_data.codigo_destino,
                "incoterms": invoice_data.incoterms,
            },
            "monotributo": {
                "categoria": invoice_data.categoria_monotributo,
                "actividad": invoice_data.actividad_monotributo,
            },
            "actividades": {
                "codigo": invoice_data.codigo_actividad,
                "descripcion": invoice_data.descripcion_actividad,
                "detalle": invoice_data.actividades,
            },
            "vendedor": invoice_data.vendedor,
            "remitos": invoice_data.remitos,
            "ordenes_pedidos": {
                "numero_orden_compra": invoice_data.numero_orden_compra,
                "numero_presupuesto": invoice_data.numero_presupuesto,
                "numero_pedido": invoice_data.numero_pedido,
                "numero_contrato": invoice_data.numero_contrato,
            },
            "condiciones_comerciales": invoice_data.condiciones_comerciales,
            "liquidacion_iva": invoice_data.liquidacion_iva,
            "certificados_timbrado": {
                "numero_certificado_digital": invoice_data.numero_certificado_digital,
                "fecha_timbrado": invoice_data.fecha_timbrado,
                "numero_timbrado": invoice_data.numero_timbrado,
                "codigo_barras": invoice_data.codigo_barras,
            },
            "fechas_adicionales": {
                "fecha_servicio_desde": invoice_data.fecha_servicio_desde,
                "fecha_servicio_hasta": invoice_data.fecha_servicio_hasta,
                "fecha_vencimiento_pago": invoice_data.fecha_vencimiento_pago,
            },
            "verificacion_calculos": {
                "total_calculado": invoice_data.total_calculado,
                "total_extraido": invoice_data.importe_total,
                "diferencia": invoice_data.diferencia_calculo,
                "productos_cantidad": invoice_data.productos_cantidad,
            },
            "estadisticas_extraccion": {
                "campos_extraidos": invoice_data.campos_extraidos,
                "campos_faltantes": invoice_data.campos_faltantes,
                "completitud": (
                    f"{(invoice_data.campos_extraidos / 8 * 100):.1f}%"
                    if invoice_data.campos_extraidos > 0
                    else "0%"
                ),
            },
        }
        if invoice_data.cae_numero or invoice_data.cuit_emisor:
            try:
                result["validacion_afip"] = self.validation_service.validate_invoice_afip(result)
            except Exception as e:
                logger.warning(f"Error en validación AFIP: {e}")
                result["validacion_afip"] = {
                    "is_valid": False,
                    "errors": [f"Error en validación: {str(e)}"],
                    "warnings": [],
                }
        return result
