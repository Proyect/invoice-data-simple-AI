"""
Servicio especializado para extracción de datos de facturas AFIP/ARCA
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class AFIPInvoiceData:
    """Estructura de datos para facturas AFIP mejorada"""
    # Información del comprobante
    tipo_comprobante: str = ""
    codigo_comprobante: str = ""  # A, B, C, E, M
    punto_venta: str = ""
    numero_comprobante: str = ""
    fecha_emision: str = ""
    fecha_vencimiento: str = ""
    
    # Información del emisor
    razon_social_emisor: str = ""
    nombre_fantasia: str = ""
    domicilio_comercial: str = ""
    codigo_postal: str = ""
    localidad: str = ""
    provincia: str = ""
    cuit_emisor: str = ""
    condicion_iva_emisor: str = ""
    numero_ingresos_brutos: str = ""
    periodo_facturado_desde: str = ""
    periodo_facturado_hasta: str = ""
    
    # Información del comprador
    cuit_comprador: str = ""
    razon_social_comprador: str = ""
    domicilio_comprador: str = ""
    condicion_iva_comprador: str = ""
    condicion_venta: str = ""
    ingresos_brutos: str = ""
    fecha_inicio_actividades: str = ""
    
    # Productos/Servicios
    productos: List[Dict[str, Any]] = None
    
    # IVA y Alícuotas
    alicuotas_iva: List[Dict[str, Any]] = None
    importe_iva: str = ""
    importe_iva_21: str = ""
    importe_iva_10_5: str = ""
    importe_iva_27: str = ""
    importe_iva_0: str = ""
    
    # Impuestos y Tributos
    importe_otros_tributos: str = ""
    detalle_otros_tributos: List[Dict[str, Any]] = None
    importe_impuestos_internos: str = ""
    importe_percepciones_iva: str = ""
    importe_percepciones_iibb: str = ""
    importe_percepciones_municipales: str = ""
    
    # Totales
    subtotal: str = ""
    subtotal_neto: str = ""
    importe_exento: str = ""
    importe_no_gravado: str = ""
    importe_total: str = ""
    
    # Información AFIP
    cae_numero: str = ""
    fecha_vencimiento_cae: str = ""
    pagina_actual: str = ""
    total_paginas: str = ""
    codigo_qr: str = ""
    
    # Retenciones detalladas
    retenciones: List[Dict[str, Any]] = None
    importe_retenciones_iva: str = ""
    importe_retenciones_iibb: str = ""
    importe_retenciones_ganancias: str = ""
    importe_retenciones_suss: str = ""
    importe_retenciones_otros: str = ""
    
    # Percepciones detalladas
    percepciones: List[Dict[str, Any]] = None
    detalle_percepciones_iva: List[Dict[str, Any]] = None
    detalle_percepciones_iibb: List[Dict[str, Any]] = None
    detalle_percepciones_municipales: List[Dict[str, Any]] = None
    
    # Información de pagos
    pagos: List[Dict[str, Any]] = None
    importe_pagado: str = ""
    importe_pendiente: str = ""
    fecha_ultimo_pago: str = ""
    metodo_pago: str = ""
    numero_cheque: str = ""
    banco_cheque: str = ""
    numero_transferencia: str = ""
    
    # Comprobantes relacionados
    comprobantes_relacionados: List[Dict[str, Any]] = None
    nota_credito_relacionada: str = ""
    nota_debito_relacionada: str = ""
    factura_original: str = ""
    
    # Información de exportación
    es_exportacion: bool = False
    codigo_destino: str = ""
    codigo_destino_expo: str = ""
    idioma_comprobante: str = ""
    incoterms: str = ""
    codigo_destino_mercaderia: str = ""
    
    # Información de monotributo
    categoria_monotributo: str = ""
    actividad_monotributo: str = ""
    
    # Información de actividades
    actividades: List[Dict[str, Any]] = None
    codigo_actividad: str = ""
    descripcion_actividad: str = ""
    
    # Información de vendedor (si es diferente del emisor)
    vendedor: Dict[str, Any] = None
    cuit_vendedor: str = ""
    razon_social_vendedor: str = ""
    
    # Información de remitos
    remitos: List[Dict[str, Any]] = None
    
    # Información de órdenes y pedidos
    numero_orden_compra: str = ""
    numero_presupuesto: str = ""
    numero_pedido: str = ""
    numero_contrato: str = ""
    
    # Información adicional
    numero_remito: str = ""
    forma_pago: str = ""
    observaciones: str = ""
    punto_entrega: str = ""
    informacion_transporte: Dict[str, Any] = None
    
    # Condiciones comerciales
    condiciones_comerciales: Dict[str, Any] = None
    plazo_pago: str = ""
    descuento_global: str = ""
    recargo_global: str = ""
    tipo_cambio: str = ""
    moneda: str = ""
    
    # Información de liquidación de IVA
    liquidacion_iva: Dict[str, Any] = None
    periodo_liquidacion: str = ""
    
    # Información de certificados y timbrado
    numero_certificado_digital: str = ""
    fecha_timbrado: str = ""
    numero_timbrado: str = ""
    codigo_barras: str = ""
    
    # Información de fechas adicionales
    fecha_servicio_desde: str = ""
    fecha_servicio_hasta: str = ""
    fecha_vencimiento_pago: str = ""
    
    # Campos calculados y verificaciones
    total_calculado: str = ""
    diferencia_calculo: str = ""
    productos_cantidad: int = 0
    campos_extraidos: int = 0
    campos_faltantes: List[str] = None
    
    def __post_init__(self):
        if self.productos is None:
            self.productos = []
        if self.alicuotas_iva is None:
            self.alicuotas_iva = []
        if self.detalle_otros_tributos is None:
            self.detalle_otros_tributos = []
        if self.informacion_transporte is None:
            self.informacion_transporte = {}
        if self.retenciones is None:
            self.retenciones = []
        if self.percepciones is None:
            self.percepciones = []
        if self.detalle_percepciones_iva is None:
            self.detalle_percepciones_iva = []
        if self.detalle_percepciones_iibb is None:
            self.detalle_percepciones_iibb = []
        if self.detalle_percepciones_municipales is None:
            self.detalle_percepciones_municipales = []
        if self.pagos is None:
            self.pagos = []
        if self.comprobantes_relacionados is None:
            self.comprobantes_relacionados = []
        if self.actividades is None:
            self.actividades = []
        if self.remitos is None:
            self.remitos = []
        if self.vendedor is None:
            self.vendedor = {}
        if self.condiciones_comerciales is None:
            self.condiciones_comerciales = {}
        if self.liquidacion_iva is None:
            self.liquidacion_iva = {}
        if self.campos_faltantes is None:
            self.campos_faltantes = []

class AFIPInvoiceExtractionService:
    """
    Servicio especializado para extraer datos de facturas AFIP/ARCA
    """
    
    def __init__(
        self,
        validation_service=None,
        specialized_ocr=None,
        universal_validation=None
    ):
        """
        Inicializar servicio con dependencias inyectadas.
        
        Args:
            validation_service: Instancia de AFIPValidationService (opcional)
            specialized_ocr: Instancia de SpecializedOCRService (opcional)
            universal_validation: Instancia de UniversalValidationService (opcional)
        """
        # Inyectar dependencias o crear instancias si no se proporcionan
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
        
        # Patrones regex mejorados para facturas AFIP con mayor precisión
        self.patterns = {
            # Información del comprobante - Patrones más flexibles
            'punto_venta': [
                r'Punto\s+de\s+Venta:\s*(\d{4,5})',
                r'Pto\.?\s*Vta\.?:\s*(\d{4,5})',
                r'P\.V\.:\s*(\d{4,5})',
                r'PV:\s*(\d{4,5})'
            ],
            'numero_comprobante': [
                r'Comp\.?\s*Nro\.?:\s*(\d+)',
                r'Nro\.?\s*Comp\.?:\s*(\d+)',
                r'Número:\s*(\d+)',
                r'Numero:\s*(\d+)'
            ],
            'fecha_emision': [
                r'Fecha\s+de\s+Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Fecha\s+Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            'fecha_vencimiento': [
                r'Fecha\s+de\s+Vto\.?\s*para\s+el\s+pago:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Vto\.?\s*para\s+el\s+pago:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Fecha\s+de\s+Vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            
            # CUIT - Múltiples formatos y validación
            'cuit': [
                r'(\d{2}-\d{8}-\d{1})',
                r'(\d{2}\.\d{8}\.\d{1})',
                r'(\d{11})'
            ],
            
            # Razón social - Más flexible
            'razon_social_emisor': [
                r'Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)',
                r'Razón\s+Social:\s*([^\n\r]+)',
                r'Razon\s+Social:\s*([^\n\r]+)'
            ],
            'domicilio_comercial': [
                r'Domicilio\s+Comercial:\s*([^\n\r]+?)(?=\n|Condición|CUIT|$)',
                r'Domicilio\s+Comercial:\s*([^\n\r]+)',
                r'Domicilio:\s*([^\n\r]+)'
            ],
            'condicion_iva_emisor': [
                r'Condición\s+frente\s+al\s+IVA:\s*([^\n\r]+?)(?=\n|Período|CUIT|$)',
                r'Condición\s+IVA:\s*([^\n\r]+)',
                r'Condicion\s+IVA:\s*([^\n\r]+)'
            ],
            'periodo_desde': [
                r'Período\s+Facturado\s+Desde:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Periodo\s+Desde:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Desde:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            'periodo_hasta': [
                r'Hasta:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Hasta\s+el:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            
            # Información del comprador - Más flexible
            'razon_social_comprador': [
                r'Apellido\s+y\s+Nombre\s*/\s*Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)',
                r'Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)',
                r'Nombre\s+y\s+Apellido:\s*([^\n\r]+)',
                r'Cliente:\s*([^\n\r]+)'
            ],
            'domicilio_comprador': [
                r'Domicilio:\s*([^\n\r]+?)(?=\n|CUIT|Condición|$)',
                r'Dirección:\s*([^\n\r]+)',
                r'Dir\.:\s*([^\n\r]+)'
            ],
            'condicion_iva_comprador': [
                r'Condición\s+frente\s+al\s+IVA:\s*([^\n\r]+?)(?=\n|Condición|CUIT|$)',
                r'Condición\s+IVA:\s*([^\n\r]+)',
                r'IVA:\s*([^\n\r]+)'
            ],
            'condicion_venta': [
                r'Condición\s+de\s+venta:\s*([^\n\r]+?)(?=\n|CUIT|Ingresos|$)',
                r'Condicion\s+venta:\s*([^\n\r]+)',
                r'Forma\s+de\s+pago:\s*([^\n\r]+)'
            ],
            'ingresos_brutos': [
                r'Ingresos\s+Brutos:\s*([^\n\r]+?)(?=\n|Fecha|CUIT|$)',
                r'Ing\.\s+Brutos:\s*([^\n\r]+)',
                r'IIBB:\s*([^\n\r]+)'
            ],
            'fecha_inicio_actividades': [
                r'Fecha\s+de\s+Inicio\s+de\s+Actividades:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Inicio\s+Actividades:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Fecha\s+Inicio:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            
            # Totales - Más precisos
            'subtotal': [
                r'Subtotal:\s*\$?\s*([\d,\.]+)',
                r'Sub\s+Total:\s*\$?\s*([\d,\.]+)',
                r'Subtotal\s+Neto:\s*\$?\s*([\d,\.]+)'
            ],
            'importe_otros_tributos': [
                r'Importe\s+Otros\s+Tributos:\s*\$?\s*([\d,\.]+)',
                r'Otros\s+Tributos:\s*\$?\s*([\d,\.]+)',
                r'Tributos:\s*\$?\s*([\d,\.]+)'
            ],
            'importe_total': [
                r'Importe\s+Total:\s*\$?\s*([\d,\.]+)',
                r'Total:\s*\$?\s*([\d,\.]+)',
                r'TOTAL:\s*\$?\s*([\d,\.]+)'
            ],
            
            # Información AFIP - Patrones mejorados para CAE
            'cae_numero': [
                r'CAE\s+N°:\s*(\d{14})',
                r'CAE\s+N°:\s*(\d{13,15})',  # Permite 13-15 dígitos
                r'CAE:\s*(\d{14})',
                r'CAE:\s*(\d{13,15})',
                r'C\.A\.E\.\s*N°:\s*(\d{14})',
                r'C\.A\.E\.\s*N°:\s*(\d{13,15})',
                r'Código\s+de\s+Autorización\s+Electrónica:\s*(\d{14})',
                r'CAE\s*Nro:\s*(\d{14})',
                r'CAE\s*Nro:\s*(\d{13,15})',
                # Patrones más flexibles para OCR con errores
                r'CAE\s*[N°n°]\s*:\s*([0-9\s]{13,16})',  # Permite espacios
                r'CAE\s*[N°n°]\s*:\s*([0-9\-]{13,16})',  # Permite guiones
            ],
            'fecha_vencimiento_cae': [
                r'Fecha\s+de\s+Vto\.?\s*de\s+CAE:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'Vto\.?\s+CAE:\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'CAE\s+Vto\.?:\s*(\d{1,2}/\d{1,2}/\d{4})'
            ],
            'pagina_info': [
                r'Pág\.?\s*(\d+)/(\d+)',
                r'Pag\.?\s*(\d+)/(\d+)',
                r'Página\s*(\d+)/(\d+)',
                r'Page\s*(\d+)/(\d+)'
            ],
        }
        
        # Tipos de comprobante AFIP (completos)
        self.tipos_comprobante = {
            'A': 'Factura A',
            'B': 'Factura B',
            'C': 'Factura C',
            'E': 'Factura E',
            'M': 'Factura M',
        }
        
        # Patrones adicionales para IVA y alícuotas
        self.patterns.update({
            'codigo_comprobante': [
                r'COD\.?\s*(\d+)\s*([A-E]|M)',
                r'Código:\s*(\d+)\s*([A-E]|M)',
                r'Comprobante\s+([A-E]|M)',
                r'Factura\s+([A-E]|M)',
            ],
            'nombre_fantasia': [
                r'Nombre\s+de\s+Fantasía:\s*([^\n\r]+)',
                r'Fantasia:\s*([^\n\r]+)',
            ],
            'codigo_postal': [
                r'C\.P\.:\s*([A-Z]?\d{4}[A-Z]{0,3})',
                r'Código\s+Postal:\s*([A-Z]?\d{4}[A-Z]{0,3})',
                r'CP:\s*([A-Z]?\d{4}[A-Z]{0,3})',
            ],
            'localidad': [
                r'Localidad:\s*([^\n\r]+?)(?=\n|Provincia|C\.P\.|$)',
                r'Ciudad:\s*([^\n\r]+)',
            ],
            'provincia': [
                r'Provincia:\s*([^\n\r]+?)(?=\n|C\.P\.|$)',
            ],
            'numero_ingresos_brutos': [
                r'Nro\.?\s*Ing\.?\s*Brutos:\s*([^\n\r]+)',
                r'Ingresos\s+Brutos\s+Nro\.?:\s*([^\n\r]+)',
            ],
            # IVA y Alícuotas
            'importe_iva': [
                r'Importe\s+IVA:\s*\$?\s*([\d,\.]+)',
                r'IVA:\s*\$?\s*([\d,\.]+)',
                r'Total\s+IVA:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_iva_21': [
                r'IVA\s+21%:\s*\$?\s*([\d,\.]+)',
                r'21%:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_iva_10_5': [
                r'IVA\s+10\.5%:\s*\$?\s*([\d,\.]+)',
                r'10\.5%:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_iva_27': [
                r'IVA\s+27%:\s*\$?\s*([\d,\.]+)',
                r'27%:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_iva_0': [
                r'IVA\s+0%:\s*\$?\s*([\d,\.]+)',
                r'Exento:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_exento': [
                r'Importe\s+Exento:\s*\$?\s*([\d,\.]+)',
                r'Exento:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_no_gravado': [
                r'Importe\s+No\s+Gravado:\s*\$?\s*([\d,\.]+)',
                r'No\s+Gravado:\s*\$?\s*([\d,\.]+)',
            ],
            'subtotal_neto': [
                r'Subtotal\s+Neto:\s*\$?\s*([\d,\.]+)',
                r'Neto:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_percepciones_iva': [
                r'Percepciones\s+IVA:\s*\$?\s*([\d,\.]+)',
                r'Percep\.\s+IVA:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_percepciones_iibb': [
                r'Percepciones\s+IIBB:\s*\$?\s*([\d,\.]+)',
                r'Percep\.\s+IIBB:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_percepciones_municipales': [
                r'Percepciones\s+Municipales:\s*\$?\s*([\d,\.]+)',
                r'Percep\.\s+Mun\.:\s*\$?\s*([\d,\.]+)',
            ],
            'importe_impuestos_internos': [
                r'Impuestos\s+Internos:\s*\$?\s*([\d,\.]+)',
                r'Imp\.\s+Int\.:\s*\$?\s*([\d,\.]+)',
            ],
            'codigo_qr': [
                r'QR:\s*([A-Z0-9]+)',
                r'Código\s+QR:\s*([A-Z0-9]+)',
            ],
            # Información adicional
            'numero_remito': [
                r'Remito\s+N°:\s*([A-Z0-9\-]+)',
                r'Remito:\s*([A-Z0-9\-]+)',
                r'Nro\.?\s*Remito:\s*([A-Z0-9\-]+)',
            ],
            'forma_pago': [
                r'Forma\s+de\s+Pago:\s*([^\n\r]+)',
                r'Forma\s+Pago:\s*([^\n\r]+)',
                r'Pago:\s*([^\n\r]+)',
            ],
            'observaciones': [
                r'Observaciones:\s*([^\n\r]+(?:\n[^\n\r]+)*)',
                r'Notas:\s*([^\n\r]+(?:\n[^\n\r]+)*)',
                r'Obs\.:\s*([^\n\r]+)',
            ],
            'punto_entrega': [
                r'Punto\s+de\s+Entrega:\s*([^\n\r]+)',
                r'Entrega:\s*([^\n\r]+)',
            ],
        })
    
    def extract_afip_invoice_data(self, text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae datos específicos de facturas AFIP/ARCA
        
        Args:
            text: Texto extraído del documento
            image_path: Ruta de la imagen original (para OCR especializado)
            
        Returns:
            Dict con los datos estructurados
        """
        try:
            logger.info("Iniciando extracción de datos AFIP")
            
            # Crear objeto de datos
            invoice_data = AFIPInvoiceData()
            
            # Extraer información del comprobante
            self._extract_comprobante_info(text, invoice_data)
            
            # Extraer información del emisor
            self._extract_emisor_info(text, invoice_data)
            
            # Extraer información del comprador
            self._extract_comprador_info(text, invoice_data)
            
            # Extraer productos/servicios
            self._extract_productos(text, invoice_data)
            
            # Extraer IVA y alícuotas
            self._extract_iva_alicuotas(text, invoice_data)
            
            # Extraer impuestos y tributos
            self._extract_impuestos_tributos(text, invoice_data)
            
            # Extraer totales
            self._extract_totales(text, invoice_data)
            
            # Extraer información AFIP
            self._extract_afip_info(text, invoice_data)
            
            # Extraer retenciones detalladas
            self._extract_retenciones(text, invoice_data)
            
            # Extraer percepciones detalladas
            self._extract_percepciones_detalladas(text, invoice_data)
            
            # Extraer información de pagos
            self._extract_pagos(text, invoice_data)
            
            # Extraer comprobantes relacionados
            self._extract_comprobantes_relacionados(text, invoice_data)
            
            # Extraer información de exportación
            self._extract_exportacion(text, invoice_data)
            
            # Extraer información de monotributo
            self._extract_monotributo(text, invoice_data)
            
            # Extraer información de actividades
            self._extract_actividades(text, invoice_data)
            
            # Extraer información de vendedor
            self._extract_vendedor(text, invoice_data)
            
            # Extraer información de remitos
            self._extract_remitos(text, invoice_data)
            
            # Extraer órdenes y pedidos
            self._extract_ordenes_pedidos(text, invoice_data)
            
            # Extraer condiciones comerciales
            self._extract_condiciones_comerciales(text, invoice_data)
            
            # Extraer información de liquidación IVA
            self._extract_liquidacion_iva(text, invoice_data)
            
            # Extraer información de certificados y timbrado
            self._extract_certificados_timbrado(text, invoice_data)
            
            # Extraer fechas adicionales
            self._extract_fechas_adicionales(text, invoice_data)
            
            # Si tenemos imagen, usar OCR especializado para campos críticos
            if image_path:
                self._enhance_with_specialized_ocr(image_path, invoice_data)
            
            # Calcular campos extraídos y faltantes
            self._calcular_estadisticas(invoice_data)
            
            # Convertir a diccionario
            result = self._to_dict(invoice_data)
            
            logger.info(f"Datos AFIP extraídos: {invoice_data.campos_extraidos} campos, {len(invoice_data.campos_faltantes)} faltantes")
            return result
            
        except Exception as e:
            logger.error(f"Error extrayendo datos AFIP: {e}")
            return {}
    
    def _extract_comprobante_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información del comprobante con múltiples patrones"""
        
        # Código de comprobante (buscar letra A, B, C, E, M)
        codigo_match = self._extract_with_multiple_patterns(text, 'codigo_comprobante')
        if codigo_match:
            # Extraer la letra del código
            codigo_letra = re.search(r'([A-E]|M)', codigo_match, re.IGNORECASE)
            if codigo_letra:
                invoice_data.codigo_comprobante = codigo_letra.group(1).upper()
                invoice_data.tipo_comprobante = self.tipos_comprobante.get(
                    invoice_data.codigo_comprobante, 
                    f"Comprobante {invoice_data.codigo_comprobante}"
                )
        
        # Si no se encontró, buscar directamente en el texto
        if not invoice_data.codigo_comprobante:
            for codigo, nombre in self.tipos_comprobante.items():
                if re.search(rf'Factura\s+{codigo}|Comprobante\s+{codigo}|COD\.?\s*{codigo}', text, re.IGNORECASE):
                    invoice_data.codigo_comprobante = codigo
                    invoice_data.tipo_comprobante = nombre
                    break
        
        # Punto de venta - Probar múltiples patrones
        invoice_data.punto_venta = self._extract_with_multiple_patterns(text, 'punto_venta')
        
        # Número de comprobante - Probar múltiples patrones
        invoice_data.numero_comprobante = self._extract_with_multiple_patterns(text, 'numero_comprobante')
        
        # Fecha de emisión - Probar múltiples patrones
        invoice_data.fecha_emision = self._extract_with_multiple_patterns(text, 'fecha_emision')
        
        # Fecha de vencimiento - Probar múltiples patrones
        invoice_data.fecha_vencimiento = self._extract_with_multiple_patterns(text, 'fecha_vencimiento')
    
    def _extract_with_multiple_patterns(self, text: str, pattern_name: str) -> str:
        """
        Extraer datos usando múltiples patrones regex
        
        Args:
            text: Texto a buscar
            pattern_name: Nombre del patrón en self.patterns
            
        Returns:
            str: Primer match exitoso o string vacío
        """
        if pattern_name not in self.patterns:
            return ""
        
        patterns = self.patterns[pattern_name]
        
        # Si es una lista, probar cada patrón
        if isinstance(patterns, list):
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1).strip()
                    # Validar el resultado si es necesario
                    if self._validate_extracted_data(pattern_name, result):
                        logger.info(f"Patrón {pattern_name} exitoso: {result}")
                        return result
        
        # Si es un string único, usarlo directamente
        elif isinstance(patterns, str):
            match = re.search(patterns, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result = match.group(1).strip()
                if self._validate_extracted_data(pattern_name, result):
                    logger.info(f"Patrón {pattern_name} exitoso: {result}")
                    return result
        
        logger.warning(f"No se encontró patrón {pattern_name}")
        return ""
    
    def _validate_extracted_data(self, field_name: str, value: str) -> bool:
        """
        Validar datos extraídos según el tipo de campo
        
        Args:
            field_name: Nombre del campo
            value: Valor extraído
            
        Returns:
            bool: True si el valor es válido
        """
        if not value or value.strip() == "":
            return False
        
        # Validaciones específicas por campo
        if field_name == 'cuit':
            # Validar formato CUIT
            return self._validate_cuit(value)
        elif field_name in ['fecha_emision', 'fecha_vencimiento', 'periodo_desde', 'periodo_hasta', 'fecha_inicio_actividades']:
            # Validar formato de fecha
            return self._validate_date(value)
        elif field_name in ['punto_venta', 'numero_comprobante']:
            # Validar que sean números
            return value.isdigit()
        elif field_name in ['subtotal', 'importe_total', 'importe_otros_tributos']:
            # Validar formato de moneda
            return self._validate_currency(value)
        elif field_name == 'cae_numero':
            # Validar CAE (limpiar y validar formato)
            clean_cae = self._clean_cae_number(value)
            return self._validate_cae_format(clean_cae)
        
        return True
    
    def _validate_cuit(self, cuit: str) -> bool:
        """Validar formato y dígito verificador de CUIT mejorado"""
        try:
            # Limpiar formato
            clean_cuit = re.sub(r'[^\d]', '', cuit)
            
            if len(clean_cuit) != 11:
                return False
            
            # Validar que no sea todo ceros o números repetidos
            if clean_cuit == '0' * 11 or len(set(clean_cuit)) == 1:
                return False
            
            # Validar prefijo (debe ser 20, 23, 24, 25, 26, 27, 30, 33, 34)
            valid_prefixes = ['20', '23', '24', '25', '26', '27', '30', '33', '34']
            prefix = clean_cuit[:2]
            if prefix not in valid_prefixes:
                return False
            
            # Validar dígito verificador usando algoritmo de AFIP
            multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            check_digit = int(clean_cuit[-1])
            body = clean_cuit[:-1]
            
            total = sum(int(digit) * mult for digit, mult in zip(body, multipliers))
            remainder = total % 11
            
            # Calcular dígito verificador
            if remainder < 2:
                calculated_check = remainder
            else:
                calculated_check = 11 - remainder
            
            is_valid = calculated_check == check_digit
            
            if is_valid:
                logger.debug(f"CUIT válido: {clean_cuit}")
            else:
                logger.warning(f"CUIT inválido (dígito verificador incorrecto): {clean_cuit}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validando CUIT {cuit}: {e}")
            return False
    
    def _validate_date(self, date_str: str) -> bool:
        """Validar formato de fecha DD/MM/YYYY"""
        try:
            import datetime
            # Probar diferentes formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
            for fmt in formats:
                try:
                    datetime.datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False
    
    def _enhance_with_specialized_ocr(self, image_path: str, invoice_data: AFIPInvoiceData):
        """
        Mejorar extracción usando OCR especializado para campos críticos
        """
        try:
            logger.info("Aplicando OCR especializado para campos críticos")
            
            # Extraer CAE con OCR especializado
            if not invoice_data.cae_numero:
                logger.info("Intentando extraer CAE con OCR especializado")
                cae_result = self.specialized_ocr.extract_cae_from_invoice(image_path)
                if cae_result['cae_number'] and cae_result['confidence'] > 0.5:
                    invoice_data.cae_numero = cae_result['cae_number']
                    logger.info(f"CAE extraído con OCR especializado: {cae_result['cae_number']} (confianza: {cae_result['confidence']:.2f})")
            
            # Extraer CUITs con OCR especializado si no se encontraron
            if not invoice_data.cuit_emisor:
                logger.info("Intentando extraer CUIT emisor con OCR especializado")
                # Buscar en diferentes regiones de la imagen
                cuit_emisor = self._extract_cuit_specialized(image_path, 'emisor')
                if cuit_emisor:
                    invoice_data.cuit_emisor = cuit_emisor
                    logger.info(f"CUIT emisor extraído: {cuit_emisor}")
            
            if not invoice_data.cuit_comprador:
                logger.info("Intentando extraer CUIT comprador con OCR especializado")
                cuit_comprador = self._extract_cuit_specialized(image_path, 'comprador')
                if cuit_comprador:
                    invoice_data.cuit_comprador = cuit_comprador
                    logger.info(f"CUIT comprador extraído: {cuit_comprador}")
            
            # Extraer totales con OCR especializado si no se encontraron
            if not invoice_data.importe_total:
                logger.info("Intentando extraer importe total con OCR especializado")
                importe_total = self._extract_amount_specialized(image_path)
                if importe_total:
                    invoice_data.importe_total = importe_total
                    logger.info(f"Importe total extraído: {importe_total}")
            
        except Exception as e:
            logger.error(f"Error en OCR especializado: {e}")
    
    def _extract_cuit_specialized(self, image_path: str, position: str) -> Optional[str]:
        """
        Extraer CUIT usando OCR especializado
        """
        try:
            # Cargar imagen
            image = Image.open(image_path)
            width, height = image.size
            
            # Definir regiones donde buscar CUITs según la posición
            if position == 'emisor':
                # CUIT emisor generalmente está en la parte izquierda
                regions = [
                    (0, height//4, width//2, height//2),  # Parte izquierda superior
                    (0, height//3, width//2, height//3),  # Parte izquierda media
                ]
            else:  # comprador
                # CUIT comprador generalmente está en la parte derecha
                regions = [
                    (width//2, height//4, width//2, height//2),  # Parte derecha superior
                    (width//2, height//3, width//2, height//3),  # Parte derecha media
                ]
            
            for i, region in enumerate(regions):
                x, y, w, h = region
                cropped = image.crop((x, y, x + w, y + h))
                
                # Extraer texto de la región
                text = self.specialized_ocr.extract_small_field_from_image(cropped, 'cuit')
                
                if text and self._validate_cuit(text):
                    logger.info(f"CUIT {position} encontrado en región {i}: {text}")
                    return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo CUIT {position}: {e}")
            return None
    
    def _extract_amount_specialized(self, image_path: str) -> Optional[str]:
        """
        Extraer importe total usando OCR especializado
        """
        try:
            # Cargar imagen
            image = Image.open(image_path)
            width, height = image.size
            
            # Buscar en la parte inferior derecha donde suelen estar los totales
            regions = [
                (width//2, height*3//4, width//2, height//4),  # Parte inferior derecha
                (width*2//3, height*2//3, width//3, height//3),  # Esquina inferior derecha
            ]
            
            for i, region in enumerate(regions):
                x, y, w, h = region
                cropped = image.crop((x, y, x + w, y + h))
                
                # Extraer texto de la región
                text = self.specialized_ocr.extract_small_field_from_image(cropped, 'amount')
                
                if text and self._validate_currency(text):
                    logger.info(f"Importe total encontrado en región {i}: {text}")
                    return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo importe total: {e}")
            return None
    
    def _validate_currency(self, amount_str: str) -> bool:
        """Validar formato de moneda"""
        try:
            # Permitir formatos como: 1000.00, 1,000.00, 1000,00
            clean_amount = re.sub(r'[^\d,\.]', '', amount_str)
            return bool(re.match(r'^\d{1,3}([.,]\d{3})*([.,]\d{2})?$', clean_amount))
        except Exception:
            return False
    
    def _clean_cae_number(self, cae_str: str) -> str:
        """Limpiar número de CAE de espacios, guiones y caracteres especiales"""
        try:
            # Remover espacios, guiones y caracteres no numéricos
            clean_cae = re.sub(r'[^\d]', '', cae_str)
            return clean_cae
        except Exception:
            return ""
    
    def _validate_cae_format(self, cae: str) -> bool:
        """Validar formato del CAE mejorado"""
        try:
            # CAE debe tener exactamente 14 dígitos
            if len(cae) != 14:
                logger.warning(f"CAE con longitud incorrecta: {len(cae)} (esperado: 14)")
                return False
            
            # Debe ser numérico
            if not cae.isdigit():
                logger.warning(f"CAE contiene caracteres no numéricos: {cae}")
                return False
            
            # Validar que no sea todo ceros
            if cae == '0' * 14:
                logger.warning("CAE es todo ceros")
                return False
            
            # Validar rango de fechas (los primeros dígitos indican fecha)
            # CAE tiene formato: AAAAMMDDHHMMSS (año, mes, día, hora, min, seg, miliseg)
            year = int(cae[:4])
            month = int(cae[4:6])
            day = int(cae[6:8])
            hour = int(cae[8:10])
            minute = int(cae[10:12])
            second = int(cae[12:14])
            
            # Validar año (debe estar en rango razonable)
            current_year = datetime.now().year
            if year < 2000 or year > current_year + 1:
                logger.warning(f"CAE con año fuera de rango: {year}")
                return False
            
            # Validar mes
            if month < 1 or month > 12:
                logger.warning(f"CAE con mes inválido: {month}")
                return False
            
            # Validar día (considerar meses con diferentes días)
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # Año bisiesto
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                days_in_month[1] = 29
            
            if day < 1 or day > days_in_month[month - 1]:
                logger.warning(f"CAE con día inválido: {day} para mes {month}")
                return False
            
            # Validar hora
            if hour > 23:
                logger.warning(f"CAE con hora inválida: {hour}")
                return False
            
            # Validar minuto
            if minute > 59:
                logger.warning(f"CAE con minuto inválido: {minute}")
                return False
            
            # Validar segundo
            if second > 59:
                logger.warning(f"CAE con segundo inválido: {second}")
                return False
            
            logger.debug(f"CAE válido: {cae}")
            return True
            
        except ValueError as e:
            logger.error(f"Error parseando CAE {cae}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validando CAE {cae}: {e}")
            return False
    
    def _calcular_y_verificar_totales(self, invoice_data: AFIPInvoiceData) -> tuple:
        """
        Calcular total desde productos y verificar contra totales extraídos
        
        Returns:
            tuple: (total_calculado, diferencia_calculo)
        """
        try:
            total_calculado = 0.0
            
            # Sumar subtotales de productos
            for producto in invoice_data.productos:
                try:
                    subtotal = float(producto.get('subtotal', 0))
                    total_calculado += subtotal
                except (ValueError, TypeError):
                    continue
            
            # Sumar IVA total si existe
            if invoice_data.importe_iva:
                try:
                    total_calculado += float(invoice_data.importe_iva.replace(',', '.'))
                except (ValueError, TypeError):
                    pass
            
            # Sumar otros tributos
            if invoice_data.importe_otros_tributos:
                try:
                    total_calculado += float(invoice_data.importe_otros_tributos.replace(',', '.'))
                except (ValueError, TypeError):
                    pass
            
            # Comparar con total extraído
            total_extraido = 0.0
            if invoice_data.importe_total:
                try:
                    total_extraido = float(invoice_data.importe_total.replace(',', '.'))
                except (ValueError, TypeError):
                    pass
            
            diferencia = abs(total_calculado - total_extraido) if total_extraido > 0 else 0.0
            porcentaje_diferencia = (diferencia / total_extraido * 100) if total_extraido > 0 else 0.0
            
            # Log si hay diferencia significativa (>1%)
            if porcentaje_diferencia > 1.0:
                logger.warning(
                    f"Diferencia en cálculos: Calculado={total_calculado:.2f}, "
                    f"Extraído={total_extraido:.2f}, Diferencia={diferencia:.2f} ({porcentaje_diferencia:.2f}%)"
                )
            
            return (
                f"{total_calculado:.2f}",
                f"{diferencia:.2f}" if diferencia > 0.01 else "0.00"
            )
        except Exception as e:
            logger.error(f"Error calculando totales: {e}")
            return ("0.00", "0.00")
    
    def _extract_transporte_info(self, text: str) -> Dict[str, Any]:
        """Extraer información de transporte si existe"""
        transporte = {}
        
        # Patrones para información de transporte
        patterns = {
            'domicilio_entrega': [
                r'Domicilio\s+de\s+Entrega:\s*([^\n\r]+)',
                r'Dirección\s+Entrega:\s*([^\n\r]+)',
            ],
            'transportista': [
                r'Transportista:\s*([^\n\r]+)',
                r'Empresa\s+Transporte:\s*([^\n\r]+)',
            ],
            'patente_vehiculo': [
                r'Patente:\s*([A-Z]{3}\d{3})',
                r'Patente\s+Vehiculo:\s*([A-Z]{3}\d{3})',
            ],
        }
        
        for campo, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    transporte[campo] = match.group(1).strip()
                    break
        
        return transporte
    
    def _extract_emisor_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información del emisor con múltiples patrones"""
        
        # Razón social del emisor
        invoice_data.razon_social_emisor = self._extract_with_multiple_patterns(text, 'razon_social_emisor')
        
        # Nombre de fantasía
        invoice_data.nombre_fantasia = self._extract_with_multiple_patterns(text, 'nombre_fantasia')
        
        # Domicilio comercial
        invoice_data.domicilio_comercial = self._extract_with_multiple_patterns(text, 'domicilio_comercial')
        
        # Código postal
        invoice_data.codigo_postal = self._extract_with_multiple_patterns(text, 'codigo_postal')
        
        # Localidad
        invoice_data.localidad = self._extract_with_multiple_patterns(text, 'localidad')
        
        # Provincia
        invoice_data.provincia = self._extract_with_multiple_patterns(text, 'provincia')
        
        # Condición frente al IVA del emisor
        invoice_data.condicion_iva_emisor = self._extract_with_multiple_patterns(text, 'condicion_iva_emisor')
        
        # Número de ingresos brutos
        invoice_data.numero_ingresos_brutos = self._extract_with_multiple_patterns(text, 'numero_ingresos_brutos')
        
        # Período facturado
        invoice_data.periodo_facturado_desde = self._extract_with_multiple_patterns(text, 'periodo_desde')
        invoice_data.periodo_facturado_hasta = self._extract_with_multiple_patterns(text, 'periodo_hasta')
        
        # CUIT del emisor - Buscar todos los CUITs y validar
        cuit_matches = []
        for pattern in self.patterns['cuit']:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._validate_cuit(match):
                    cuit_matches.append(match)
        
        if cuit_matches:
            invoice_data.cuit_emisor = cuit_matches[0]
    
    def _extract_comprador_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información del comprador con múltiples patrones"""
        
        # Razón social del comprador
        invoice_data.razon_social_comprador = self._extract_with_multiple_patterns(text, 'razon_social_comprador')
        
        # Domicilio del comprador
        invoice_data.domicilio_comprador = self._extract_with_multiple_patterns(text, 'domicilio_comprador')
        
        # Condición frente al IVA del comprador
        invoice_data.condicion_iva_comprador = self._extract_with_multiple_patterns(text, 'condicion_iva_comprador')
        
        # Condición de venta
        invoice_data.condicion_venta = self._extract_with_multiple_patterns(text, 'condicion_venta')
        
        # Ingresos brutos
        invoice_data.ingresos_brutos = self._extract_with_multiple_patterns(text, 'ingresos_brutos')
        
        # Fecha de inicio de actividades
        invoice_data.fecha_inicio_actividades = self._extract_with_multiple_patterns(text, 'fecha_inicio_actividades')
        
        # CUIT del comprador - Buscar todos los CUITs válidos
        cuit_matches = []
        for pattern in self.patterns['cuit']:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._validate_cuit(match):
                    cuit_matches.append(match)
        
        # Usar el segundo CUIT si hay más de uno
        if len(cuit_matches) > 1:
            invoice_data.cuit_comprador = cuit_matches[1]
        elif len(cuit_matches) == 1 and not invoice_data.cuit_emisor:
            # Si solo hay uno y no se asignó al emisor, asignarlo al comprador
            invoice_data.cuit_comprador = cuit_matches[0]
    
    def _extract_productos(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de productos/servicios con patrones mejorados y cálculos"""
        
        # Buscar sección de productos (entre "Productos" o "Detalle" y "Totales" o "IVA")
        productos_section = self._extract_productos_section(text)
        
        if not productos_section:
            productos_section = text  # Si no se encuentra sección, usar todo el texto
        
        # Patrones mejorados para productos
        # Patrón 1: Formato completo con código, descripción, cantidad, unidad, precio, IVA, bonif, subtotal
        producto_pattern_1 = r'(\w+)\s+([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)\s+([\d,\.]+)\s+(\d+[,\.]\d+%?)?\s*([\d,\.]+)?\s*(\d+[,\.]\d+)?\s*([\d,\.]+)?\s*([\d,\.]+)'
        
        # Patrón 2: Formato con tabla (separadores | o espacios múltiples)
        producto_pattern_2 = r'\|?\s*(\w+)?\s*\|?\s*([^\|]+?)\s*\|?\s*(\d+[,\.]\d+)\s*\|?\s*(\w+)\s*\|?\s*([\d,\.]+)\s*\|?\s*(\d+[,\.]\d+%?)?\s*\|?\s*([\d,\.]+)?\s*\|?\s*([\d,\.]+)?\s*\|?\s*([\d,\.]+)'
        
        # Patrón 3: Formato simplificado (descripción, cantidad, precio, total)
        producto_pattern_3 = r'([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)?\s+([\d,\.]+)\s+([\d,\.]+)'
        
        # Patrón 4: Formato con líneas numeradas
        producto_pattern_4 = r'(\d+)\.\s+([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)?\s+([\d,\.]+)\s+([\d,\.]+)'
        
        matches = []
        matches.extend(re.findall(producto_pattern_1, productos_section))
        matches.extend(re.findall(producto_pattern_2, productos_section))
        matches.extend(re.findall(producto_pattern_3, productos_section))
        matches.extend(re.findall(producto_pattern_4, productos_section))
        
        productos_unicos = {}  # Para evitar duplicados
        
        for match in matches:
            try:
                producto = self._parse_producto_match(match)
                
                if producto and producto.get('descripcion'):
                    # Usar descripción como clave para evitar duplicados
                    key = producto['descripcion'][:100].strip().lower()
                    if key not in productos_unicos:
                        productos_unicos[key] = producto
                        # Calcular campos faltantes
                        producto = self._calcular_campos_producto(producto)
                        invoice_data.productos.append(producto)
                        logger.debug(f"Producto extraído: {producto['descripcion'][:50]}")
            except Exception as e:
                logger.warning(f"Error extrayendo producto: {e}")
                continue
        
        invoice_data.productos_cantidad = len(invoice_data.productos)
        logger.info(f"Total de productos extraídos: {invoice_data.productos_cantidad}")
    
    def _extract_productos_section(self, text: str) -> str:
        """Extraer la sección de productos del texto"""
        # Buscar entre "Productos", "Detalle", "Items" y "Totales", "IVA", "Subtotal"
        patterns = [
            r'(?:Productos|Detalle|Items)[\s\S]*?(?=Totales|IVA|Subtotal|Importe\s+Total|$)',
            r'(?:Código|Descripción)[\s\S]*?(?=Totales|IVA|Subtotal|Importe\s+Total|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(0)
        
        return ""
    
    def _parse_producto_match(self, match: tuple) -> Optional[Dict[str, Any]]:
        """Parsear un match de producto a diccionario estructurado"""
        try:
            # Determinar qué patrón se usó según la cantidad de grupos
            if len(match) >= 10:
                # Patrón 1 completo
                return {
                    'codigo': match[0].strip() if match[0] else '',
                    'descripcion': match[1].strip(),
                    'cantidad': self._normalize_number(match[2]),
                    'unidad_medida': match[3].strip() if match[3] else 'UN',
                    'precio_unitario': self._normalize_number(match[4]),
                    'porcentaje_iva': self._normalize_percentage(match[5]) if len(match) > 5 and match[5] else '21',
                    'importe_iva': self._normalize_number(match[6]) if len(match) > 6 and match[6] else '',
                    'porcentaje_bonificacion': self._normalize_percentage(match[7]) if len(match) > 7 and match[7] else '0',
                    'importe_bonificacion': self._normalize_number(match[8]) if len(match) > 8 and match[8] else '0',
                    'subtotal': self._normalize_number(match[9]) if len(match) > 9 else '',
                }
            elif len(match) >= 8:
                # Patrón 2 con tabla
                return {
                    'codigo': match[0].strip() if match[0] else '',
                    'descripcion': match[1].strip(),
                    'cantidad': self._normalize_number(match[2]),
                    'unidad_medida': match[3].strip() if match[3] else 'UN',
                    'precio_unitario': self._normalize_number(match[4]),
                    'porcentaje_iva': self._normalize_percentage(match[5]) if len(match) > 5 and match[5] else '21',
                    'importe_iva': self._normalize_number(match[6]) if len(match) > 6 and match[6] else '',
                    'subtotal': self._normalize_number(match[7]) if len(match) > 7 else '',
                    'porcentaje_bonificacion': '0',
                    'importe_bonificacion': '0',
                }
            elif len(match) >= 5:
                # Patrón 3 o 4 simplificado
                return {
                    'codigo': match[0].strip() if len(match) > 5 else '',  # Solo si es patrón 4
                    'descripcion': match[1] if len(match) > 5 else match[0],
                    'cantidad': self._normalize_number(match[2] if len(match) > 5 else match[1]),
                    'unidad_medida': match[3].strip() if len(match) > 5 and match[3] else 'UN',
                    'precio_unitario': self._normalize_number(match[4] if len(match) > 5 else match[2]),
                    'subtotal': self._normalize_number(match[5] if len(match) > 5 else match[3]),
                    'porcentaje_iva': '21',  # Valor por defecto
                    'importe_iva': '',
                    'porcentaje_bonificacion': '0',
                    'importe_bonificacion': '0',
                }
            else:
                return None
        except Exception as e:
            logger.warning(f"Error parseando match de producto: {e}")
            return None
    
    def _calcular_campos_producto(self, producto: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular campos faltantes del producto"""
        try:
            cantidad = float(producto.get('cantidad', 0))
            precio_unitario = float(producto.get('precio_unitario', 0))
            porcentaje_iva = float(producto.get('porcentaje_iva', 21))
            
            # Calcular subtotal si no existe
            if not producto.get('subtotal') or producto['subtotal'] == '':
                subtotal_sin_iva = cantidad * precio_unitario
                producto['subtotal_sin_iva'] = f"{subtotal_sin_iva:.2f}"
                
                # Aplicar bonificación si existe
                importe_bonificacion = float(producto.get('importe_bonificacion', 0))
                subtotal_con_bonif = subtotal_sin_iva - importe_bonificacion
                
                # Calcular IVA
                importe_iva = subtotal_con_bonif * (porcentaje_iva / 100)
                producto['importe_iva'] = f"{importe_iva:.2f}"
                
                # Subtotal final
                subtotal_final = subtotal_con_bonif + importe_iva
                producto['subtotal'] = f"{subtotal_final:.2f}"
            else:
                # Si ya existe subtotal, calcular IVA si falta
                subtotal = float(producto['subtotal'])
                if not producto.get('importe_iva') or producto['importe_iva'] == '':
                    subtotal_sin_iva = subtotal / (1 + porcentaje_iva / 100)
                    importe_iva = subtotal - subtotal_sin_iva
                    producto['importe_iva'] = f"{importe_iva:.2f}"
                    producto['subtotal_sin_iva'] = f"{subtotal_sin_iva:.2f}"
            
            return producto
        except Exception as e:
            logger.warning(f"Error calculando campos de producto: {e}")
            return producto
    
    def _normalize_number(self, value: str) -> str:
        """Normalizar número reemplazando comas por puntos"""
        if not value:
            return '0'
        return value.replace(',', '.').strip()
    
    def _normalize_percentage(self, value: str) -> str:
        """Normalizar porcentaje removiendo el símbolo %"""
        if not value:
            return '0'
        return value.replace('%', '').replace(',', '.').strip()
    
    def _extract_iva_alicuotas(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de IVA y alícuotas"""
        
        # Importe total de IVA
        invoice_data.importe_iva = self._extract_with_multiple_patterns(text, 'importe_iva')
        
        # IVA por alícuota
        invoice_data.importe_iva_21 = self._extract_with_multiple_patterns(text, 'importe_iva_21')
        invoice_data.importe_iva_10_5 = self._extract_with_multiple_patterns(text, 'importe_iva_10_5')
        invoice_data.importe_iva_27 = self._extract_with_multiple_patterns(text, 'importe_iva_27')
        invoice_data.importe_iva_0 = self._extract_with_multiple_patterns(text, 'importe_iva_0')
        
        # Extraer tabla de alícuotas IVA
        # Patrón para encontrar líneas de alícuotas: Base Imponible | Alícuota | Importe
        alicuota_pattern = r'([\d,\.]+)\s+(\d+[,\.]\d+%?)\s+([\d,\.]+)'
        alicuota_matches = re.findall(alicuota_pattern, text)
        
        for match in alicuota_matches:
            try:
                alicuota = {
                    'base_imponible': match[0].replace(',', '.'),
                    'alicuota': match[1].replace(',', '.').replace('%', ''),
                    'importe': match[2].replace(',', '.')
                }
                invoice_data.alicuotas_iva.append(alicuota)
            except Exception as e:
                logger.warning(f"Error extrayendo alícuota: {e}")
                continue
    
    def _extract_impuestos_tributos(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de impuestos y tributos"""
        
        # Importe otros tributos
        invoice_data.importe_otros_tributos = self._extract_with_multiple_patterns(text, 'importe_otros_tributos')
        
        # Impuestos internos
        invoice_data.importe_impuestos_internos = self._extract_with_multiple_patterns(text, 'importe_impuestos_internos')
        
        # Percepciones
        invoice_data.importe_percepciones_iva = self._extract_with_multiple_patterns(text, 'importe_percepciones_iva')
        invoice_data.importe_percepciones_iibb = self._extract_with_multiple_patterns(text, 'importe_percepciones_iibb')
        invoice_data.importe_percepciones_municipales = self._extract_with_multiple_patterns(text, 'importe_percepciones_municipales')
        
        # Extraer detalle de otros tributos si existe
        tributo_pattern = r'([^\n\r]+?)\s+([\d,\.]+)'
        tributo_matches = re.findall(tributo_pattern, text)
        
        for match in tributo_matches:
            if any(keyword in match[0].upper() for keyword in ['TRIBUTO', 'IMPUESTO', 'PERCEPCION', 'RETENCION']):
                try:
                    tributo = {
                        'descripcion': match[0].strip(),
                        'importe': match[1].replace(',', '.')
                    }
                    invoice_data.detalle_otros_tributos.append(tributo)
                except Exception as e:
                    logger.warning(f"Error extrayendo tributo: {e}")
                    continue
    
    def _extract_totales(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer totales con múltiples patrones y verificación de cálculos"""
        
        # Subtotal
        invoice_data.subtotal = self._extract_with_multiple_patterns(text, 'subtotal')
        
        # Subtotal neto
        invoice_data.subtotal_neto = self._extract_with_multiple_patterns(text, 'subtotal_neto')
        
        # Importe exento
        invoice_data.importe_exento = self._extract_with_multiple_patterns(text, 'importe_exento')
        
        # Importe no gravado
        invoice_data.importe_no_gravado = self._extract_with_multiple_patterns(text, 'importe_no_gravado')
        
        # Importe total
        invoice_data.importe_total = self._extract_with_multiple_patterns(text, 'importe_total')
        
        # Calcular total desde productos y verificar
        invoice_data.total_calculado, invoice_data.diferencia_calculo = self._calcular_y_verificar_totales(invoice_data)
    
    def _extract_afip_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información específica de AFIP con múltiples patrones"""
        
        # CAE
        invoice_data.cae_numero = self._extract_with_multiple_patterns(text, 'cae_numero')
        
        # Fecha de vencimiento del CAE
        invoice_data.fecha_vencimiento_cae = self._extract_with_multiple_patterns(text, 'fecha_vencimiento_cae')
        
        # Información de páginas
        pagina_result = self._extract_with_multiple_patterns(text, 'pagina_info')
        if pagina_result:
            # El patrón de páginas devuelve "1/1", necesitamos separarlo
            if '/' in pagina_result:
                parts = pagina_result.split('/')
                if len(parts) == 2:
                    invoice_data.pagina_actual = parts[0].strip()
                    invoice_data.total_paginas = parts[1].strip()
        
        # Código QR
        invoice_data.codigo_qr = self._extract_with_multiple_patterns(text, 'codigo_qr')
        
        # Información adicional
        invoice_data.numero_remito = self._extract_with_multiple_patterns(text, 'numero_remito')
        invoice_data.forma_pago = self._extract_with_multiple_patterns(text, 'forma_pago')
        invoice_data.observaciones = self._extract_with_multiple_patterns(text, 'observaciones')
        invoice_data.punto_entrega = self._extract_with_multiple_patterns(text, 'punto_entrega')
        
        # Información de transporte
        invoice_data.informacion_transporte = self._extract_transporte_info(text)
    
    def _extract_retenciones(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de retenciones"""
        invoice_data.importe_retenciones_iva = self._extract_with_multiple_patterns(text, 'retenciones_iva')
        invoice_data.importe_retenciones_iibb = self._extract_with_multiple_patterns(text, 'retenciones_iibb')
        invoice_data.importe_retenciones_ganancias = self._extract_with_multiple_patterns(text, 'retenciones_ganancias')
        invoice_data.importe_retenciones_suss = self._extract_with_multiple_patterns(text, 'retenciones_suss')
        
        # Extraer tabla de retenciones
        retencion_pattern = r'([^\n\r]+?)\s+([\d,\.]+)'
        matches = re.findall(retencion_pattern, text)
        for match in matches:
            if any(keyword in match[0].upper() for keyword in ['RETENCION', 'RETENCIÓN']):
                try:
                    retencion = {
                        'descripcion': match[0].strip(),
                        'importe': match[1].replace(',', '.')
                    }
                    invoice_data.retenciones.append(retencion)
                except Exception as e:
                    logger.warning(f"Error extrayendo retención: {e}")
    
    def _extract_percepciones_detalladas(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer percepciones detalladas"""
        # Extraer tabla de percepciones IVA
        percepcion_iva_pattern = r'IVA[^\n\r]*?([\d,\.]+)'
        matches = re.findall(percepcion_iva_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                percepcion = {
                    'tipo': 'IVA',
                    'importe': match.replace(',', '.')
                }
                invoice_data.detalle_percepciones_iva.append(percepcion)
            except Exception as e:
                logger.warning(f"Error extrayendo percepción IVA: {e}")
        
        # Extraer tabla de percepciones IIBB
        percepcion_iibb_pattern = r'IIBB[^\n\r]*?([\d,\.]+)'
        matches = re.findall(percepcion_iibb_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                percepcion = {
                    'tipo': 'IIBB',
                    'importe': match.replace(',', '.')
                }
                invoice_data.detalle_percepciones_iibb.append(percepcion)
            except Exception as e:
                logger.warning(f"Error extrayendo percepción IIBB: {e}")
    
    def _extract_pagos(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de pagos"""
        invoice_data.importe_pagado = self._extract_with_multiple_patterns(text, 'importe_pagado')
        invoice_data.importe_pendiente = self._extract_with_multiple_patterns(text, 'importe_pendiente')
        invoice_data.fecha_ultimo_pago = self._extract_with_multiple_patterns(text, 'fecha_ultimo_pago')
        invoice_data.metodo_pago = invoice_data.forma_pago  # Ya extraído
        invoice_data.numero_cheque = self._extract_with_multiple_patterns(text, 'numero_cheque')
        invoice_data.banco_cheque = self._extract_with_multiple_patterns(text, 'banco_cheque')
        invoice_data.numero_transferencia = self._extract_with_multiple_patterns(text, 'numero_transferencia')
    
    def _extract_comprobantes_relacionados(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer comprobantes relacionados"""
        invoice_data.nota_credito_relacionada = self._extract_with_multiple_patterns(text, 'nota_credito')
        invoice_data.nota_debito_relacionada = self._extract_with_multiple_patterns(text, 'nota_debito')
        invoice_data.factura_original = self._extract_with_multiple_patterns(text, 'factura_original')
    
    def _extract_exportacion(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de exportación"""
        if 'EXPORTACION' in text.upper() or 'EXPORTACIÓN' in text.upper():
            invoice_data.es_exportacion = True
        invoice_data.codigo_destino = self._extract_with_multiple_patterns(text, 'codigo_destino')
        invoice_data.incoterms = self._extract_with_multiple_patterns(text, 'incoterms')
    
    def _extract_monotributo(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de monotributo"""
        invoice_data.categoria_monotributo = self._extract_with_multiple_patterns(text, 'categoria_monotributo')
        if invoice_data.categoria_monotributo:
            # Buscar actividad asociada
            actividad_match = re.search(r'Actividad[^\n\r]*?([A-Z])', text, re.IGNORECASE)
            if actividad_match:
                invoice_data.actividad_monotributo = actividad_match.group(1)
    
    def _extract_actividades(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de actividades"""
        invoice_data.codigo_actividad = self._extract_with_multiple_patterns(text, 'codigo_actividad')
        if invoice_data.codigo_actividad:
            # Buscar descripción de actividad
            actividad_desc_pattern = r'Actividad[^\n\r]*?([^\n\r]+)'
            match = re.search(actividad_desc_pattern, text, re.IGNORECASE)
            if match:
                invoice_data.descripcion_actividad = match.group(1).strip()
    
    def _extract_vendedor(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de vendedor"""
        invoice_data.cuit_vendedor = self._extract_with_multiple_patterns(text, 'cuit_vendedor')
        invoice_data.razon_social_vendedor = self._extract_with_multiple_patterns(text, 'razon_social_vendedor')
        if invoice_data.cuit_vendedor or invoice_data.razon_social_vendedor:
            invoice_data.vendedor = {
                'cuit': invoice_data.cuit_vendedor,
                'razon_social': invoice_data.razon_social_vendedor
            }
    
    def _extract_remitos(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de remitos"""
        if invoice_data.numero_remito:
            invoice_data.remitos.append({
                'numero': invoice_data.numero_remito,
                'tipo': 'remito'
            })
        # Buscar remitos adicionales
        remito_pattern = r'Remito[^\n\r]*?([A-Z0-9\-]+)'
        matches = re.findall(remito_pattern, text, re.IGNORECASE)
        for match in matches:
            if match != invoice_data.numero_remito:
                invoice_data.remitos.append({
                    'numero': match,
                    'tipo': 'remito'
                })
    
    def _extract_ordenes_pedidos(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de órdenes y pedidos"""
        invoice_data.numero_orden_compra = self._extract_with_multiple_patterns(text, 'numero_orden_compra')
        invoice_data.numero_presupuesto = self._extract_with_multiple_patterns(text, 'numero_presupuesto')
        invoice_data.numero_pedido = self._extract_with_multiple_patterns(text, 'numero_pedido')
        invoice_data.numero_contrato = self._extract_with_multiple_patterns(text, 'numero_contrato')
    
    def _extract_condiciones_comerciales(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer condiciones comerciales"""
        invoice_data.plazo_pago = self._extract_with_multiple_patterns(text, 'plazo_pago')
        invoice_data.descuento_global = self._extract_with_multiple_patterns(text, 'descuento_global')
        invoice_data.recargo_global = self._extract_with_multiple_patterns(text, 'recargo_global')
        invoice_data.tipo_cambio = self._extract_with_multiple_patterns(text, 'tipo_cambio')
        invoice_data.moneda = self._extract_with_multiple_patterns(text, 'moneda')
        if not invoice_data.moneda:
            invoice_data.moneda = 'ARS'  # Por defecto pesos argentinos
        
        invoice_data.condiciones_comerciales = {
            'plazo_pago': invoice_data.plazo_pago,
            'descuento_global': invoice_data.descuento_global,
            'recargo_global': invoice_data.recargo_global,
            'tipo_cambio': invoice_data.tipo_cambio,
            'moneda': invoice_data.moneda
        }
    
    def _extract_liquidacion_iva(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de liquidación de IVA"""
        invoice_data.periodo_liquidacion = self._extract_with_multiple_patterns(text, 'periodo_liquidacion')
        if invoice_data.periodo_liquidacion:
            invoice_data.liquidacion_iva = {
                'periodo': invoice_data.periodo_liquidacion,
                'importe_iva': invoice_data.importe_iva
            }
    
    def _extract_certificados_timbrado(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información de certificados y timbrado"""
        invoice_data.numero_certificado_digital = self._extract_with_multiple_patterns(text, 'numero_certificado_digital')
        invoice_data.fecha_timbrado = self._extract_with_multiple_patterns(text, 'fecha_timbrado')
        invoice_data.numero_timbrado = self._extract_with_multiple_patterns(text, 'numero_timbrado')
        invoice_data.codigo_barras = self._extract_with_multiple_patterns(text, 'codigo_barras')
    
    def _extract_fechas_adicionales(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer fechas adicionales"""
        invoice_data.fecha_servicio_desde = self._extract_with_multiple_patterns(text, 'fecha_servicio_desde')
        invoice_data.fecha_servicio_hasta = self._extract_with_multiple_patterns(text, 'fecha_servicio_hasta')
        invoice_data.fecha_vencimiento_pago = self._extract_with_multiple_patterns(text, 'fecha_vencimiento_pago')
    
    def _calcular_estadisticas(self, invoice_data: AFIPInvoiceData):
        """Calcular estadísticas de campos extraídos y faltantes"""
        # Contar campos no vacíos
        campos_importantes = [
            invoice_data.tipo_comprobante, invoice_data.punto_venta, invoice_data.numero_comprobante,
            invoice_data.cuit_emisor, invoice_data.razon_social_emisor, invoice_data.importe_total,
            invoice_data.cae_numero, invoice_data.fecha_emision
        ]
        invoice_data.campos_extraidos = sum(1 for campo in campos_importantes if campo)
        
        # Identificar campos faltantes críticos
        campos_criticos = {
            'cae_numero': invoice_data.cae_numero,
            'cuit_emisor': invoice_data.cuit_emisor,
            'importe_total': invoice_data.importe_total,
            'fecha_emision': invoice_data.fecha_emision,
            'punto_venta': invoice_data.punto_venta,
            'numero_comprobante': invoice_data.numero_comprobante
        }
        
        invoice_data.campos_faltantes = [
            campo for campo, valor in campos_criticos.items() if not valor
        ]
    
    def _to_dict(self, invoice_data: AFIPInvoiceData) -> Dict[str, Any]:
        """Convertir objeto a diccionario"""
        
        result = {
            'tipo_documento': 'factura_afip',
            'informacion_comprobante': {
                'tipo': invoice_data.tipo_comprobante,
                'punto_venta': invoice_data.punto_venta,
                'numero': invoice_data.numero_comprobante,
                'fecha_emision': invoice_data.fecha_emision,
                'fecha_vencimiento': invoice_data.fecha_vencimiento,
            },
            'emisor': {
                'razon_social': invoice_data.razon_social_emisor,
                'nombre_fantasia': invoice_data.nombre_fantasia,
                'domicilio': invoice_data.domicilio_comercial,
                'codigo_postal': invoice_data.codigo_postal,
                'localidad': invoice_data.localidad,
                'provincia': invoice_data.provincia,
                'cuit': invoice_data.cuit_emisor,
                'condicion_iva': invoice_data.condicion_iva_emisor,
                'numero_ingresos_brutos': invoice_data.numero_ingresos_brutos,
                'periodo_desde': invoice_data.periodo_facturado_desde,
                'periodo_hasta': invoice_data.periodo_facturado_hasta,
            },
            'comprador': {
                'cuit': invoice_data.cuit_comprador,
                'razon_social': invoice_data.razon_social_comprador,
                'domicilio': invoice_data.domicilio_comprador,
                'condicion_iva': invoice_data.condicion_iva_comprador,
                'condicion_venta': invoice_data.condicion_venta,
                'ingresos_brutos': invoice_data.ingresos_brutos,
                'fecha_inicio_actividades': invoice_data.fecha_inicio_actividades,
            },
            'productos': invoice_data.productos,
            'iva': {
                'importe_total': invoice_data.importe_iva,
                'importe_21': invoice_data.importe_iva_21,
                'importe_10_5': invoice_data.importe_iva_10_5,
                'importe_27': invoice_data.importe_iva_27,
                'importe_0': invoice_data.importe_iva_0,
                'alicuotas': invoice_data.alicuotas_iva,
            },
            'impuestos_tributos': {
                'otros_tributos': invoice_data.importe_otros_tributos,
                'detalle_otros_tributos': invoice_data.detalle_otros_tributos,
                'impuestos_internos': invoice_data.importe_impuestos_internos,
                'percepciones_iva': invoice_data.importe_percepciones_iva,
                'percepciones_iibb': invoice_data.importe_percepciones_iibb,
                'percepciones_municipales': invoice_data.importe_percepciones_municipales,
            },
            'totales': {
                'subtotal': invoice_data.subtotal,
                'subtotal_neto': invoice_data.subtotal_neto,
                'importe_exento': invoice_data.importe_exento,
                'importe_no_gravado': invoice_data.importe_no_gravado,
                'otros_tributos': invoice_data.importe_otros_tributos,
                'total': invoice_data.importe_total,
            },
            'afip': {
                'cae_numero': invoice_data.cae_numero,
                'cae_vencimiento': invoice_data.fecha_vencimiento_cae,
                'pagina_actual': invoice_data.pagina_actual,
                'total_paginas': invoice_data.total_paginas,
                'codigo_qr': invoice_data.codigo_qr,
            },
            'informacion_adicional': {
                'numero_remito': invoice_data.numero_remito,
                'forma_pago': invoice_data.forma_pago,
                'observaciones': invoice_data.observaciones,
                'punto_entrega': invoice_data.punto_entrega,
                'informacion_transporte': invoice_data.informacion_transporte,
            },
            'retenciones': {
                'importe_retenciones_iva': invoice_data.importe_retenciones_iva,
                'importe_retenciones_iibb': invoice_data.importe_retenciones_iibb,
                'importe_retenciones_ganancias': invoice_data.importe_retenciones_ganancias,
                'importe_retenciones_suss': invoice_data.importe_retenciones_suss,
                'detalle': invoice_data.retenciones,
            },
            'percepciones_detalladas': {
                'detalle_iva': invoice_data.detalle_percepciones_iva,
                'detalle_iibb': invoice_data.detalle_percepciones_iibb,
                'detalle_municipales': invoice_data.detalle_percepciones_municipales,
            },
            'pagos': {
                'importe_pagado': invoice_data.importe_pagado,
                'importe_pendiente': invoice_data.importe_pendiente,
                'fecha_ultimo_pago': invoice_data.fecha_ultimo_pago,
                'metodo_pago': invoice_data.metodo_pago,
                'numero_cheque': invoice_data.numero_cheque,
                'banco_cheque': invoice_data.banco_cheque,
                'numero_transferencia': invoice_data.numero_transferencia,
                'detalle': invoice_data.pagos,
            },
            'comprobantes_relacionados': {
                'nota_credito': invoice_data.nota_credito_relacionada,
                'nota_debito': invoice_data.nota_debito_relacionada,
                'factura_original': invoice_data.factura_original,
                'detalle': invoice_data.comprobantes_relacionados,
            },
            'exportacion': {
                'es_exportacion': invoice_data.es_exportacion,
                'codigo_destino': invoice_data.codigo_destino,
                'incoterms': invoice_data.incoterms,
            },
            'monotributo': {
                'categoria': invoice_data.categoria_monotributo,
                'actividad': invoice_data.actividad_monotributo,
            },
            'actividades': {
                'codigo': invoice_data.codigo_actividad,
                'descripcion': invoice_data.descripcion_actividad,
                'detalle': invoice_data.actividades,
            },
            'vendedor': invoice_data.vendedor,
            'remitos': invoice_data.remitos,
            'ordenes_pedidos': {
                'numero_orden_compra': invoice_data.numero_orden_compra,
                'numero_presupuesto': invoice_data.numero_presupuesto,
                'numero_pedido': invoice_data.numero_pedido,
                'numero_contrato': invoice_data.numero_contrato,
            },
            'condiciones_comerciales': invoice_data.condiciones_comerciales,
            'liquidacion_iva': invoice_data.liquidacion_iva,
            'certificados_timbrado': {
                'numero_certificado_digital': invoice_data.numero_certificado_digital,
                'fecha_timbrado': invoice_data.fecha_timbrado,
                'numero_timbrado': invoice_data.numero_timbrado,
                'codigo_barras': invoice_data.codigo_barras,
            },
            'fechas_adicionales': {
                'fecha_servicio_desde': invoice_data.fecha_servicio_desde,
                'fecha_servicio_hasta': invoice_data.fecha_servicio_hasta,
                'fecha_vencimiento_pago': invoice_data.fecha_vencimiento_pago,
            },
            'verificacion_calculos': {
                'total_calculado': invoice_data.total_calculado,
                'total_extraido': invoice_data.importe_total,
                'diferencia': invoice_data.diferencia_calculo,
                'productos_cantidad': invoice_data.productos_cantidad,
            },
            'estadisticas_extraccion': {
                'campos_extraidos': invoice_data.campos_extraidos,
                'campos_faltantes': invoice_data.campos_faltantes,
                'completitud': f"{(invoice_data.campos_extraidos / 8 * 100):.1f}%" if invoice_data.campos_extraidos > 0 else "0%",
            }
        }
        
        # Agregar validación si hay datos suficientes
        if invoice_data.cae_numero or invoice_data.cuit_emisor:
            try:
                validation_result = self.validation_service.validate_invoice_afip(result)
                result['validacion_afip'] = validation_result
                logger.info(f"Validación AFIP completada. Válida: {validation_result['is_valid']}")
            except Exception as e:
                logger.warning(f"Error en validación AFIP: {e}")
                result['validacion_afip'] = {
                    'is_valid': False,
                    'errors': [f"Error en validación: {str(e)}"],
                    'warnings': []
                }
        
        return result
