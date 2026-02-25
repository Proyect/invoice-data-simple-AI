"""
Patrones regex y constantes para extracción de facturas AFIP/ARCA.
Centralizados para mantenibilidad y reutilización.
"""
from typing import Dict, List, Any

# Tipos de comprobante AFIP
TIPOS_COMPROBANTE: Dict[str, str] = {
    "A": "Factura A",
    "B": "Factura B",
    "C": "Factura C",
    "E": "Factura E",
    "M": "Factura M",
}


def get_afip_patterns() -> Dict[str, Any]:
    """Construye y devuelve el diccionario completo de patrones regex para AFIP."""
    patterns: Dict[str, Any] = {
        "punto_venta": [
            r"Punto\s+de\s+Venta:\s*(\d{4,5})",
            r"Pto\.?\s*Vta\.?:\s*(\d{4,5})",
            r"P\.V\.:\s*(\d{4,5})",
            r"PV:\s*(\d{4,5})",
        ],
        "numero_comprobante": [
            r"Comp\.?\s*Nro\.?:\s*(\d+)",
            r"Nro\.?\s*Comp\.?:\s*(\d+)",
            r"Número:\s*(\d+)",
            r"Numero:\s*(\d+)",
        ],
        "fecha_emision": [
            r"Fecha\s+de\s+Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha\s+Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Emisión:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "fecha_vencimiento": [
            r"Fecha\s+de\s+Vto\.?\s*para\s+el\s+pago:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Vto\.?\s*para\s+el\s+pago:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha\s+de\s+Vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "cuit": [
            r"(\d{2}-\d{8}-\d{1})",
            r"(\d{2}\.\d{8}\.\d{1})",
            r"(\d{11})",
        ],
        "razon_social_emisor": [
            r"Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)",
            r"Razón\s+Social:\s*([^\n\r]+)",
            r"Razon\s+Social:\s*([^\n\r]+)",
        ],
        "domicilio_comercial": [
            r"Domicilio\s+Comercial:\s*([^\n\r]+?)(?=\n|Condición|CUIT|$)",
            r"Domicilio\s+Comercial:\s*([^\n\r]+)",
            r"Domicilio:\s*([^\n\r]+)",
        ],
        "condicion_iva_emisor": [
            r"Condición\s+frente\s+al\s+IVA:\s*([^\n\r]+?)(?=\n|Período|CUIT|$)",
            r"Condición\s+IVA:\s*([^\n\r]+)",
            r"Condicion\s+IVA:\s*([^\n\r]+)",
        ],
        "periodo_desde": [
            r"Período\s+Facturado\s+Desde:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Periodo\s+Desde:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Desde:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "periodo_hasta": [
            r"Hasta:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Hasta\s+el:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "razon_social_comprador": [
            r"Apellido\s+y\s+Nombre\s*/\s*Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)",
            r"Razón\s+Social:\s*([^\n\r]+?)(?=\n|Domicilio|CUIT|$)",
            r"Nombre\s+y\s+Apellido:\s*([^\n\r]+)",
            r"Cliente:\s*([^\n\r]+)",
        ],
        "domicilio_comprador": [
            r"Domicilio:\s*([^\n\r]+?)(?=\n|CUIT|Condición|$)",
            r"Dirección:\s*([^\n\r]+)",
            r"Dir\.:\s*([^\n\r]+)",
        ],
        "condicion_iva_comprador": [
            r"Condición\s+frente\s+al\s+IVA:\s*([^\n\r]+?)(?=\n|Condición|CUIT|$)",
            r"Condición\s+IVA:\s*([^\n\r]+)",
            r"IVA:\s*([^\n\r]+)",
        ],
        "condicion_venta": [
            r"Condición\s+de\s+venta:\s*([^\n\r]+?)(?=\n|CUIT|Ingresos|$)",
            r"Condicion\s+venta:\s*([^\n\r]+)",
            r"Forma\s+de\s+pago:\s*([^\n\r]+)",
        ],
        "ingresos_brutos": [
            r"Ingresos\s+Brutos:\s*([^\n\r]+?)(?=\n|Fecha|CUIT|$)",
            r"Ing\.\s+Brutos:\s*([^\n\r]+)",
            r"IIBB:\s*([^\n\r]+)",
        ],
        "fecha_inicio_actividades": [
            r"Fecha\s+de\s+Inicio\s+de\s+Actividades:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Inicio\s+Actividades:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha\s+Inicio:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "subtotal": [
            r"Subtotal:\s*\$?\s*([\d,\.]+)",
            r"Sub\s+Total:\s*\$?\s*([\d,\.]+)",
            r"Subtotal\s+Neto:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_otros_tributos": [
            r"Importe\s+Otros\s+Tributos:\s*\$?\s*([\d,\.]+)",
            r"Otros\s+Tributos:\s*\$?\s*([\d,\.]+)",
            r"Tributos:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_total": [
            r"Importe\s+Total:\s*\$?\s*([\d,\.]+)",
            r"Total:\s*\$?\s*([\d,\.]+)",
            r"TOTAL:\s*\$?\s*([\d,\.]+)",
        ],
        "cae_numero": [
            r"CAE\s+N°:\s*(\d{14})",
            r"CAE\s+N°:\s*(\d{13,15})",
            r"CAE:\s*(\d{14})",
            r"CAE:\s*(\d{13,15})",
            r"C\.A\.E\.\s*N°:\s*(\d{14})",
            r"C\.A\.E\.\s*N°:\s*(\d{13,15})",
            r"Código\s+de\s+Autorización\s+Electrónica:\s*(\d{14})",
            r"CAE\s*Nro:\s*(\d{14})",
            r"CAE\s*Nro:\s*(\d{13,15})",
            r"CAE\s*[N°n°]\s*:\s*([0-9\s]{13,16})",
            r"CAE\s*[N°n°]\s*:\s*([0-9\-]{13,16})",
        ],
        "fecha_vencimiento_cae": [
            r"Fecha\s+de\s+Vto\.?\s*de\s+CAE:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Vto\.?\s+CAE:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"CAE\s+Vto\.?:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ],
        "pagina_info": [
            r"Pág\.?\s*(\d+)/(\d+)",
            r"Pag\.?\s*(\d+)/(\d+)",
            r"Página\s*(\d+)/(\d+)",
            r"Page\s*(\d+)/(\d+)",
        ],
    }

    # Patrones adicionales (IVA, alícuotas, etc.)
    patterns.update({
        "codigo_comprobante": [
            r"COD\.?\s*(\d+)\s*([A-E]|M)",
            r"Código:\s*(\d+)\s*([A-E]|M)",
            r"Comprobante\s+([A-E]|M)",
            r"Factura\s+([A-E]|M)",
        ],
        "nombre_fantasia": [
            r"Nombre\s+de\s+Fantasía:\s*([^\n\r]+)",
            r"Fantasia:\s*([^\n\r]+)",
        ],
        "codigo_postal": [
            r"C\.P\.:\s*([A-Z]?\d{4}[A-Z]{0,3})",
            r"Código\s+Postal:\s*([A-Z]?\d{4}[A-Z]{0,3})",
            r"CP:\s*([A-Z]?\d{4}[A-Z]{0,3})",
        ],
        "localidad": [
            r"Localidad:\s*([^\n\r]+?)(?=\n|Provincia|C\.P\.|$)",
            r"Ciudad:\s*([^\n\r]+)",
        ],
        "provincia": [
            r"Provincia:\s*([^\n\r]+?)(?=\n|C\.P\.|$)",
        ],
        "numero_ingresos_brutos": [
            r"Nro\.?\s*Ing\.?\s*Brutos:\s*([^\n\r]+)",
            r"Ingresos\s+Brutos\s+Nro\.?:\s*([^\n\r]+)",
        ],
        "importe_iva": [
            r"Importe\s+IVA:\s*\$?\s*([\d,\.]+)",
            r"IVA:\s*\$?\s*([\d,\.]+)",
            r"Total\s+IVA:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_iva_21": [
            r"IVA\s+21%:\s*\$?\s*([\d,\.]+)",
            r"21%:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_iva_10_5": [
            r"IVA\s+10\.5%:\s*\$?\s*([\d,\.]+)",
            r"10\.5%:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_iva_27": [
            r"IVA\s+27%:\s*\$?\s*([\d,\.]+)",
            r"27%:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_iva_0": [
            r"IVA\s+0%:\s*\$?\s*([\d,\.]+)",
            r"Exento:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_exento": [
            r"Importe\s+Exento:\s*\$?\s*([\d,\.]+)",
            r"Exento:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_no_gravado": [
            r"Importe\s+No\s+Gravado:\s*\$?\s*([\d,\.]+)",
            r"No\s+Gravado:\s*\$?\s*([\d,\.]+)",
        ],
        "subtotal_neto": [
            r"Subtotal\s+Neto:\s*\$?\s*([\d,\.]+)",
            r"Neto:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_percepciones_iva": [
            r"Percepciones\s+IVA:\s*\$?\s*([\d,\.]+)",
            r"Percep\.\s+IVA:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_percepciones_iibb": [
            r"Percepciones\s+IIBB:\s*\$?\s*([\d,\.]+)",
            r"Percep\.\s+IIBB:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_percepciones_municipales": [
            r"Percepciones\s+Municipales:\s*\$?\s*([\d,\.]+)",
            r"Percep\.\s+Mun\.:\s*\$?\s*([\d,\.]+)",
        ],
        "importe_impuestos_internos": [
            r"Impuestos\s+Internos:\s*\$?\s*([\d,\.]+)",
            r"Imp\.\s+Int\.:\s*\$?\s*([\d,\.]+)",
        ],
        "codigo_qr": [
            r"QR:\s*([A-Z0-9]+)",
            r"Código\s+QR:\s*([A-Z0-9]+)",
        ],
        "numero_remito": [
            r"Remito\s+N°:\s*([A-Z0-9\-]+)",
            r"Remito:\s*([A-Z0-9\-]+)",
            r"Nro\.?\s*Remito:\s*([A-Z0-9\-]+)",
        ],
        "forma_pago": [
            r"Forma\s+de\s+Pago:\s*([^\n\r]+)",
            r"Forma\s+Pago:\s*([^\n\r]+)",
            r"Pago:\s*([^\n\r]+)",
        ],
        "observaciones": [
            r"Observaciones:\s*([^\n\r]+(?:\n[^\n\r]+)*)",
            r"Notas:\s*([^\n\r]+(?:\n[^\n\r]+)*)",
            r"Obs\.:\s*([^\n\r]+)",
        ],
        "punto_entrega": [
            r"Punto\s+de\s+Entrega:\s*([^\n\r]+)",
            r"Entrega:\s*([^\n\r]+)",
        ],
        "retenciones_iva": [
            r"Retenciones?\s+IVA:\s*\$?\s*([\d,\.]+)",
        ],
        "retenciones_iibb": [
            r"Retenciones?\s+IIBB:\s*\$?\s*([\d,\.]+)",
        ],
        "retenciones_ganancias": [
            r"Retenciones?\s+Ganancias:\s*\$?\s*([\d,\.]+)",
        ],
        "retenciones_suss": [
            r"Retenciones?\s+SUSS?:\s*\$?\s*([\d,\.]+)",
        ],
    })
    return patterns
