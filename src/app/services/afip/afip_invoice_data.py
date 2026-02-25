"""
Estructura de datos para facturas AFIP/ARCA.
Extraído desde afip_invoice_extraction_service para reducir tamaño del servicio.
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class AFIPInvoiceData:
    """Estructura de datos para facturas AFIP mejorada"""
    # Información del comprobante
    tipo_comprobante: str = ""
    codigo_comprobante: str = ""
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

    # Información de vendedor
    vendedor: Dict[str, Any] = None
    cuit_vendedor: str = ""
    razon_social_vendedor: str = ""

    # Información de remitos
    remitos: List[Dict[str, Any]] = None

    # Órdenes y pedidos
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

    # Liquidación de IVA
    liquidacion_iva: Dict[str, Any] = None
    periodo_liquidacion: str = ""

    # Certificados y timbrado
    numero_certificado_digital: str = ""
    fecha_timbrado: str = ""
    numero_timbrado: str = ""
    codigo_barras: str = ""

    # Fechas adicionales
    fecha_servicio_desde: str = ""
    fecha_servicio_hasta: str = ""
    fecha_vencimiento_pago: str = ""

    # Campos calculados
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
