"""
Extracción de datos de facturas AFIP desde texto.
Usa patrones y validadores del módulo afip; sin OCR ni imagen.
"""
import re
import logging
from typing import Dict, Any, List, Optional

from .afip_invoice_data import AFIPInvoiceData
from .afip_patterns import get_afip_patterns, TIPOS_COMPROBANTE
from . import afip_validators

logger = logging.getLogger(__name__)


class AfipTextExtractor:
    """
    Extrae datos de factura AFIP desde texto plano (sin imagen).
    """

    def __init__(self):
        self.patterns = get_afip_patterns()
        self.tipos_comprobante = TIPOS_COMPROBANTE

    def extract_all(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        """Ejecuta todas las extracciones sobre el texto y rellena invoice_data."""
        self._extract_comprobante_info(text, invoice_data)
        self._extract_emisor_info(text, invoice_data)
        self._extract_comprador_info(text, invoice_data)
        self._extract_productos(text, invoice_data)
        self._extract_iva_alicuotas(text, invoice_data)
        self._extract_impuestos_tributos(text, invoice_data)
        self._extract_totales(text, invoice_data)
        self._extract_afip_info(text, invoice_data)
        self._extract_retenciones(text, invoice_data)
        self._extract_percepciones_detalladas(text, invoice_data)
        self._extract_pagos(text, invoice_data)
        self._extract_comprobantes_relacionados(text, invoice_data)
        self._extract_exportacion(text, invoice_data)
        self._extract_monotributo(text, invoice_data)
        self._extract_actividades(text, invoice_data)
        self._extract_vendedor(text, invoice_data)
        self._extract_remitos(text, invoice_data)
        self._extract_ordenes_pedidos(text, invoice_data)
        self._extract_condiciones_comerciales(text, invoice_data)
        self._extract_liquidacion_iva(text, invoice_data)
        self._extract_certificados_timbrado(text, invoice_data)
        self._extract_fechas_adicionales(text, invoice_data)
        self._calcular_estadisticas(invoice_data)

    def _extract_with_multiple_patterns(self, text: str, pattern_name: str) -> str:
        """Aplica los patrones del nombre indicado y devuelve el primer match válido."""
        if pattern_name not in self.patterns:
            return ""
        patterns = self.patterns[pattern_name]
        if isinstance(patterns, list):
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1).strip()
                    if afip_validators.validate_extracted_data(pattern_name, result):
                        return result
        elif isinstance(patterns, str):
            match = re.search(patterns, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result = match.group(1).strip()
                if afip_validators.validate_extracted_data(pattern_name, result):
                    return result
        return ""

    def _extract_comprobante_info(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        codigo_match = self._extract_with_multiple_patterns(text, "codigo_comprobante")
        if codigo_match:
            codigo_letra = re.search(r"([A-E]|M)", codigo_match, re.IGNORECASE)
            if codigo_letra:
                invoice_data.codigo_comprobante = codigo_letra.group(1).upper()
                invoice_data.tipo_comprobante = self.tipos_comprobante.get(
                    invoice_data.codigo_comprobante,
                    f"Comprobante {invoice_data.codigo_comprobante}",
                )
        if not invoice_data.codigo_comprobante:
            for codigo, nombre in self.tipos_comprobante.items():
                if re.search(rf"Factura\s+{codigo}|Comprobante\s+{codigo}|COD\.?\s*{codigo}", text, re.IGNORECASE):
                    invoice_data.codigo_comprobante = codigo
                    invoice_data.tipo_comprobante = nombre
                    break
        invoice_data.punto_venta = self._extract_with_multiple_patterns(text, "punto_venta")
        invoice_data.numero_comprobante = self._extract_with_multiple_patterns(text, "numero_comprobante")
        invoice_data.fecha_emision = self._extract_with_multiple_patterns(text, "fecha_emision")
        invoice_data.fecha_vencimiento = self._extract_with_multiple_patterns(text, "fecha_vencimiento")

    def _extract_emisor_info(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.razon_social_emisor = self._extract_with_multiple_patterns(text, "razon_social_emisor")
        invoice_data.nombre_fantasia = self._extract_with_multiple_patterns(text, "nombre_fantasia")
        invoice_data.domicilio_comercial = self._extract_with_multiple_patterns(text, "domicilio_comercial")
        invoice_data.codigo_postal = self._extract_with_multiple_patterns(text, "codigo_postal")
        invoice_data.localidad = self._extract_with_multiple_patterns(text, "localidad")
        invoice_data.provincia = self._extract_with_multiple_patterns(text, "provincia")
        invoice_data.condicion_iva_emisor = self._extract_with_multiple_patterns(text, "condicion_iva_emisor")
        invoice_data.numero_ingresos_brutos = self._extract_with_multiple_patterns(text, "numero_ingresos_brutos")
        invoice_data.periodo_facturado_desde = self._extract_with_multiple_patterns(text, "periodo_desde")
        invoice_data.periodo_facturado_hasta = self._extract_with_multiple_patterns(text, "periodo_hasta")
        cuit_matches = []
        for pattern in self.patterns["cuit"]:
            for match in re.findall(pattern, text):
                if afip_validators.validate_cuit(match):
                    cuit_matches.append(match)
        if cuit_matches:
            invoice_data.cuit_emisor = cuit_matches[0]

    def _extract_comprador_info(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.razon_social_comprador = self._extract_with_multiple_patterns(text, "razon_social_comprador")
        invoice_data.domicilio_comprador = self._extract_with_multiple_patterns(text, "domicilio_comprador")
        invoice_data.condicion_iva_comprador = self._extract_with_multiple_patterns(text, "condicion_iva_comprador")
        invoice_data.condicion_venta = self._extract_with_multiple_patterns(text, "condicion_venta")
        invoice_data.ingresos_brutos = self._extract_with_multiple_patterns(text, "ingresos_brutos")
        invoice_data.fecha_inicio_actividades = self._extract_with_multiple_patterns(text, "fecha_inicio_actividades")
        cuit_matches = []
        for pattern in self.patterns["cuit"]:
            for match in re.findall(pattern, text):
                if afip_validators.validate_cuit(match):
                    cuit_matches.append(match)
        if len(cuit_matches) > 1:
            invoice_data.cuit_comprador = cuit_matches[1]
        elif len(cuit_matches) == 1 and not invoice_data.cuit_emisor:
            invoice_data.cuit_comprador = cuit_matches[0]

    def _extract_productos_section(self, text: str) -> str:
        for pattern in [
            r"(?:Productos|Detalle|Items)[\s\S]*?(?=Totales|IVA|Subtotal|Importe\s+Total|$)",
            r"(?:Código|Descripción)[\s\S]*?(?=Totales|IVA|Subtotal|Importe\s+Total|$)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(0)
        return ""

    def _normalize_number(self, value: str) -> str:
        return (value or "0").replace(",", ".").strip()

    def _normalize_percentage(self, value: str) -> str:
        return (value or "0").replace("%", "").replace(",", ".").strip()

    def _parse_producto_match(self, match: tuple) -> Optional[Dict[str, Any]]:
        try:
            if len(match) >= 10:
                return {
                    "codigo": match[0].strip() if match[0] else "",
                    "descripcion": match[1].strip(),
                    "cantidad": self._normalize_number(match[2]),
                    "unidad_medida": match[3].strip() if match[3] else "UN",
                    "precio_unitario": self._normalize_number(match[4]),
                    "porcentaje_iva": self._normalize_percentage(match[5]) if len(match) > 5 and match[5] else "21",
                    "importe_iva": self._normalize_number(match[6]) if len(match) > 6 and match[6] else "",
                    "porcentaje_bonificacion": self._normalize_percentage(match[7]) if len(match) > 7 and match[7] else "0",
                    "importe_bonificacion": self._normalize_number(match[8]) if len(match) > 8 and match[8] else "0",
                    "subtotal": self._normalize_number(match[9]) if len(match) > 9 else "",
                }
            if len(match) >= 8:
                return {
                    "codigo": match[0].strip() if match[0] else "",
                    "descripcion": match[1].strip(),
                    "cantidad": self._normalize_number(match[2]),
                    "unidad_medida": match[3].strip() if match[3] else "UN",
                    "precio_unitario": self._normalize_number(match[4]),
                    "porcentaje_iva": self._normalize_percentage(match[5]) if len(match) > 5 and match[5] else "21",
                    "importe_iva": self._normalize_number(match[6]) if len(match) > 6 and match[6] else "",
                    "subtotal": self._normalize_number(match[7]) if len(match) > 7 else "",
                    "porcentaje_bonificacion": "0",
                    "importe_bonificacion": "0",
                }
            if len(match) >= 5:
                return {
                    "codigo": match[0].strip() if len(match) > 5 else "",
                    "descripcion": match[1] if len(match) > 5 else match[0],
                    "cantidad": self._normalize_number(match[2] if len(match) > 5 else match[1]),
                    "unidad_medida": match[3].strip() if len(match) > 5 and match[3] else "UN",
                    "precio_unitario": self._normalize_number(match[4] if len(match) > 5 else match[2]),
                    "subtotal": self._normalize_number(match[5] if len(match) > 5 else match[3]),
                    "porcentaje_iva": "21",
                    "importe_iva": "",
                    "porcentaje_bonificacion": "0",
                    "importe_bonificacion": "0",
                }
        except Exception as e:
            logger.warning(f"Error parseando match de producto: {e}")
        return None

    def _calcular_campos_producto(self, producto: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cantidad = float(producto.get("cantidad", 0))
            precio_unitario = float(producto.get("precio_unitario", 0))
            porcentaje_iva = float(producto.get("porcentaje_iva", 21))
            if not producto.get("subtotal") or producto["subtotal"] == "":
                subtotal_sin_iva = cantidad * precio_unitario
                producto["subtotal_sin_iva"] = f"{subtotal_sin_iva:.2f}"
                importe_bonificacion = float(producto.get("importe_bonificacion", 0))
                subtotal_con_bonif = subtotal_sin_iva - importe_bonificacion
                importe_iva = subtotal_con_bonif * (porcentaje_iva / 100)
                producto["importe_iva"] = f"{importe_iva:.2f}"
                producto["subtotal"] = f"{subtotal_con_bonif + importe_iva:.2f}"
            else:
                subtotal = float(producto["subtotal"])
                if not producto.get("importe_iva") or producto["importe_iva"] == "":
                    subtotal_sin_iva = subtotal / (1 + porcentaje_iva / 100)
                    producto["importe_iva"] = f"{subtotal - subtotal_sin_iva:.2f}"
                    producto["subtotal_sin_iva"] = f"{subtotal_sin_iva:.2f}"
        except Exception as e:
            logger.warning(f"Error calculando campos de producto: {e}")
        return producto

    def _extract_productos(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        section = self._extract_productos_section(text) or text
        p1 = r"(\w+)\s+([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)\s+([\d,\.]+)\s+(\d+[,\.]\d+%?)?\s*([\d,\.]+)?\s*(\d+[,\.]\d+)?\s*([\d,\.]+)?\s*([\d,\.]+)"
        p2 = r"\|?\s*(\w+)?\s*\|?\s*([^\|]+?)\s*\|?\s*(\d+[,\.]\d+)\s*\|?\s*(\w+)\s*\|?\s*([\d,\.]+)\s*\|?\s*(\d+[,\.]\d+%?)?\s*\|?\s*([\d,\.]+)?\s*\|?\s*([\d,\.]+)?\s*\|?\s*([\d,\.]+)"
        p3 = r"([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)?\s+([\d,\.]+)\s+([\d,\.]+)"
        p4 = r"(\d+)\.\s+([^\n\r]+?)\s+(\d+[,\.]\d+)\s+(\w+)?\s+([\d,\.]+)\s+([\d,\.]+)"
        matches = []
        for pattern in (p1, p2, p3, p4):
            matches.extend(re.findall(pattern, section))
        seen = {}
        for match in matches:
            producto = self._parse_producto_match(match)
            if producto and producto.get("descripcion"):
                key = producto["descripcion"][:100].strip().lower()
                if key not in seen:
                    seen[key] = True
                    producto = self._calcular_campos_producto(producto)
                    invoice_data.productos.append(producto)
        invoice_data.productos_cantidad = len(invoice_data.productos)

    def _extract_iva_alicuotas(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.importe_iva = self._extract_with_multiple_patterns(text, "importe_iva")
        invoice_data.importe_iva_21 = self._extract_with_multiple_patterns(text, "importe_iva_21")
        invoice_data.importe_iva_10_5 = self._extract_with_multiple_patterns(text, "importe_iva_10_5")
        invoice_data.importe_iva_27 = self._extract_with_multiple_patterns(text, "importe_iva_27")
        invoice_data.importe_iva_0 = self._extract_with_multiple_patterns(text, "importe_iva_0")
        for m in re.findall(r"([\d,\.]+)\s+(\d+[,\.]\d+%?)\s+([\d,\.]+)", text):
            try:
                invoice_data.alicuotas_iva.append({
                    "base_imponible": m[0].replace(",", "."),
                    "alicuota": m[1].replace(",", ".").replace("%", ""),
                    "importe": m[2].replace(",", "."),
                })
            except Exception as e:
                logger.warning(f"Error extrayendo alícuota: {e}")

    def _extract_impuestos_tributos(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.importe_otros_tributos = self._extract_with_multiple_patterns(text, "importe_otros_tributos")
        invoice_data.importe_impuestos_internos = self._extract_with_multiple_patterns(text, "importe_impuestos_internos")
        invoice_data.importe_percepciones_iva = self._extract_with_multiple_patterns(text, "importe_percepciones_iva")
        invoice_data.importe_percepciones_iibb = self._extract_with_multiple_patterns(text, "importe_percepciones_iibb")
        invoice_data.importe_percepciones_municipales = self._extract_with_multiple_patterns(text, "importe_percepciones_municipales")
        for m in re.findall(r"([^\n\r]+?)\s+([\d,\.]+)", text):
            if any(k in m[0].upper() for k in ["TRIBUTO", "IMPUESTO", "PERCEPCION", "RETENCION"]):
                try:
                    invoice_data.detalle_otros_tributos.append({
                        "descripcion": m[0].strip(),
                        "importe": m[1].replace(",", "."),
                    })
                except Exception as e:
                    logger.warning(f"Error extrayendo tributo: {e}")

    def _calcular_y_verificar_totales(self, invoice_data: AFIPInvoiceData) -> tuple:
        try:
            total_calc = 0.0
            for p in invoice_data.productos:
                try:
                    total_calc += float(p.get("subtotal", 0))
                except (ValueError, TypeError):
                    pass
            if invoice_data.importe_iva:
                try:
                    total_calc += float(invoice_data.importe_iva.replace(",", "."))
                except (ValueError, TypeError):
                    pass
            if invoice_data.importe_otros_tributos:
                try:
                    total_calc += float(invoice_data.importe_otros_tributos.replace(",", "."))
                except (ValueError, TypeError):
                    pass
            total_extraido = 0.0
            if invoice_data.importe_total:
                try:
                    total_extraido = float(invoice_data.importe_total.replace(",", "."))
                except (ValueError, TypeError):
                    pass
            diff = abs(total_calc - total_extraido) if total_extraido > 0 else 0.0
            return (f"{total_calc:.2f}", f"{diff:.2f}" if diff > 0.01 else "0.00")
        except Exception as e:
            logger.error(f"Error calculando totales: {e}")
        return ("0.00", "0.00")

    def _extract_totales(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.subtotal = self._extract_with_multiple_patterns(text, "subtotal")
        invoice_data.subtotal_neto = self._extract_with_multiple_patterns(text, "subtotal_neto")
        invoice_data.importe_exento = self._extract_with_multiple_patterns(text, "importe_exento")
        invoice_data.importe_no_gravado = self._extract_with_multiple_patterns(text, "importe_no_gravado")
        invoice_data.importe_total = self._extract_with_multiple_patterns(text, "importe_total")
        invoice_data.total_calculado, invoice_data.diferencia_calculo = self._calcular_y_verificar_totales(invoice_data)

    def _extract_transporte_info(self, text: str) -> Dict[str, Any]:
        out = {}
        for campo, pats in [
            ("domicilio_entrega", [r"Domicilio\s+de\s+Entrega:\s*([^\n\r]+)", r"Dirección\s+Entrega:\s*([^\n\r]+)"]),
            ("transportista", [r"Transportista:\s*([^\n\r]+)", r"Empresa\s+Transporte:\s*([^\n\r]+)"]),
            ("patente_vehiculo", [r"Patente:\s*([A-Z]{3}\d{3})", r"Patente\s+Vehiculo:\s*([A-Z]{3}\d{3})"]),
        ]:
            for p in pats:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    out[campo] = m.group(1).strip()
                    break
        return out

    def _extract_afip_info(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.cae_numero = self._extract_with_multiple_patterns(text, "cae_numero")
        invoice_data.fecha_vencimiento_cae = self._extract_with_multiple_patterns(text, "fecha_vencimiento_cae")
        pagina_result = self._extract_with_multiple_patterns(text, "pagina_info")
        if pagina_result and "/" in pagina_result:
            parts = pagina_result.split("/")
            if len(parts) == 2:
                invoice_data.pagina_actual = parts[0].strip()
                invoice_data.total_paginas = parts[1].strip()
        else:
            for pattern in self.patterns.get("pagina_info", []):
                m = re.search(pattern, text, re.IGNORECASE)
                if m and m.lastindex >= 2:
                    invoice_data.pagina_actual = m.group(1).strip()
                    invoice_data.total_paginas = m.group(2).strip()
                    break
        invoice_data.codigo_qr = self._extract_with_multiple_patterns(text, "codigo_qr")
        invoice_data.numero_remito = self._extract_with_multiple_patterns(text, "numero_remito")
        invoice_data.forma_pago = self._extract_with_multiple_patterns(text, "forma_pago")
        invoice_data.observaciones = self._extract_with_multiple_patterns(text, "observaciones")
        invoice_data.punto_entrega = self._extract_with_multiple_patterns(text, "punto_entrega")
        invoice_data.informacion_transporte = self._extract_transporte_info(text)

    def _extract_retenciones(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.importe_retenciones_iva = self._extract_with_multiple_patterns(text, "retenciones_iva")
        invoice_data.importe_retenciones_iibb = self._extract_with_multiple_patterns(text, "retenciones_iibb")
        invoice_data.importe_retenciones_ganancias = self._extract_with_multiple_patterns(text, "retenciones_ganancias")
        invoice_data.importe_retenciones_suss = self._extract_with_multiple_patterns(text, "retenciones_suss")
        for m in re.findall(r"([^\n\r]+?)\s+([\d,\.]+)", text):
            if "RETENCION" in m[0].upper() or "RETENCIÓN" in m[0].upper():
                try:
                    invoice_data.retenciones.append({"descripcion": m[0].strip(), "importe": m[1].replace(",", ".")})
                except Exception as e:
                    logger.warning(f"Error extrayendo retención: {e}")

    def _extract_percepciones_detalladas(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        for m in re.findall(r"IVA[^\n\r]*?([\d,\.]+)", text, re.IGNORECASE):
            try:
                invoice_data.detalle_percepciones_iva.append({"tipo": "IVA", "importe": m.replace(",", ".")})
            except Exception as e:
                logger.warning(f"Error extrayendo percepción IVA: {e}")
        for m in re.findall(r"IIBB[^\n\r]*?([\d,\.]+)", text, re.IGNORECASE):
            try:
                invoice_data.detalle_percepciones_iibb.append({"tipo": "IIBB", "importe": m.replace(",", ".")})
            except Exception as e:
                logger.warning(f"Error extrayendo percepción IIBB: {e}")

    def _extract_pagos(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.importe_pagado = self._extract_with_multiple_patterns(text, "importe_pagado")
        invoice_data.importe_pendiente = self._extract_with_multiple_patterns(text, "importe_pendiente")
        invoice_data.fecha_ultimo_pago = self._extract_with_multiple_patterns(text, "fecha_ultimo_pago")
        invoice_data.metodo_pago = invoice_data.forma_pago
        invoice_data.numero_cheque = self._extract_with_multiple_patterns(text, "numero_cheque")
        invoice_data.banco_cheque = self._extract_with_multiple_patterns(text, "banco_cheque")
        invoice_data.numero_transferencia = self._extract_with_multiple_patterns(text, "numero_transferencia")

    def _extract_comprobantes_relacionados(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.nota_credito_relacionada = self._extract_with_multiple_patterns(text, "nota_credito")
        invoice_data.nota_debito_relacionada = self._extract_with_multiple_patterns(text, "nota_debito")
        invoice_data.factura_original = self._extract_with_multiple_patterns(text, "factura_original")

    def _extract_exportacion(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.es_exportacion = "EXPORTACION" in text.upper() or "EXPORTACIÓN" in text.upper()
        invoice_data.codigo_destino = self._extract_with_multiple_patterns(text, "codigo_destino")
        invoice_data.incoterms = self._extract_with_multiple_patterns(text, "incoterms")

    def _extract_monotributo(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.categoria_monotributo = self._extract_with_multiple_patterns(text, "categoria_monotributo")
        if invoice_data.categoria_monotributo:
            m = re.search(r"Actividad[^\n\r]*?([A-Z])", text, re.IGNORECASE)
            if m:
                invoice_data.actividad_monotributo = m.group(1)

    def _extract_actividades(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.codigo_actividad = self._extract_with_multiple_patterns(text, "codigo_actividad")
        if invoice_data.codigo_actividad:
            m = re.search(r"Actividad[^\n\r]*?([^\n\r]+)", text, re.IGNORECASE)
            if m:
                invoice_data.descripcion_actividad = m.group(1).strip()

    def _extract_vendedor(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.cuit_vendedor = self._extract_with_multiple_patterns(text, "cuit_vendedor")
        invoice_data.razon_social_vendedor = self._extract_with_multiple_patterns(text, "razon_social_vendedor")
        if invoice_data.cuit_vendedor or invoice_data.razon_social_vendedor:
            invoice_data.vendedor = {
                "cuit": invoice_data.cuit_vendedor,
                "razon_social": invoice_data.razon_social_vendedor,
            }

    def _extract_remitos(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        if invoice_data.numero_remito:
            invoice_data.remitos.append({"numero": invoice_data.numero_remito, "tipo": "remito"})
        for m in re.findall(r"Remito[^\n\r]*?([A-Z0-9\-]+)", text, re.IGNORECASE):
            if m != invoice_data.numero_remito:
                invoice_data.remitos.append({"numero": m, "tipo": "remito"})

    def _extract_ordenes_pedidos(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.numero_orden_compra = self._extract_with_multiple_patterns(text, "numero_orden_compra")
        invoice_data.numero_presupuesto = self._extract_with_multiple_patterns(text, "numero_presupuesto")
        invoice_data.numero_pedido = self._extract_with_multiple_patterns(text, "numero_pedido")
        invoice_data.numero_contrato = self._extract_with_multiple_patterns(text, "numero_contrato")

    def _extract_condiciones_comerciales(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.plazo_pago = self._extract_with_multiple_patterns(text, "plazo_pago")
        invoice_data.descuento_global = self._extract_with_multiple_patterns(text, "descuento_global")
        invoice_data.recargo_global = self._extract_with_multiple_patterns(text, "recargo_global")
        invoice_data.tipo_cambio = self._extract_with_multiple_patterns(text, "tipo_cambio")
        invoice_data.moneda = self._extract_with_multiple_patterns(text, "moneda") or "ARS"
        invoice_data.condiciones_comerciales = {
            "plazo_pago": invoice_data.plazo_pago,
            "descuento_global": invoice_data.descuento_global,
            "recargo_global": invoice_data.recargo_global,
            "tipo_cambio": invoice_data.tipo_cambio,
            "moneda": invoice_data.moneda,
        }

    def _extract_liquidacion_iva(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.periodo_liquidacion = self._extract_with_multiple_patterns(text, "periodo_liquidacion")
        if invoice_data.periodo_liquidacion:
            invoice_data.liquidacion_iva = {
                "periodo": invoice_data.periodo_liquidacion,
                "importe_iva": invoice_data.importe_iva,
            }

    def _extract_certificados_timbrado(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.numero_certificado_digital = self._extract_with_multiple_patterns(text, "numero_certificado_digital")
        invoice_data.fecha_timbrado = self._extract_with_multiple_patterns(text, "fecha_timbrado")
        invoice_data.numero_timbrado = self._extract_with_multiple_patterns(text, "numero_timbrado")
        invoice_data.codigo_barras = self._extract_with_multiple_patterns(text, "codigo_barras")

    def _extract_fechas_adicionales(self, text: str, invoice_data: AFIPInvoiceData) -> None:
        invoice_data.fecha_servicio_desde = self._extract_with_multiple_patterns(text, "fecha_servicio_desde")
        invoice_data.fecha_servicio_hasta = self._extract_with_multiple_patterns(text, "fecha_servicio_hasta")
        invoice_data.fecha_vencimiento_pago = self._extract_with_multiple_patterns(text, "fecha_vencimiento_pago")

    def _calcular_estadisticas(self, invoice_data: AFIPInvoiceData) -> None:
        campos_importantes = [
            invoice_data.tipo_comprobante,
            invoice_data.punto_venta,
            invoice_data.numero_comprobante,
            invoice_data.cuit_emisor,
            invoice_data.razon_social_emisor,
            invoice_data.importe_total,
            invoice_data.cae_numero,
            invoice_data.fecha_emision,
        ]
        invoice_data.campos_extraidos = sum(1 for c in campos_importantes if c)
        campos_criticos = {
            "cae_numero": invoice_data.cae_numero,
            "cuit_emisor": invoice_data.cuit_emisor,
            "importe_total": invoice_data.importe_total,
            "fecha_emision": invoice_data.fecha_emision,
            "punto_venta": invoice_data.punto_venta,
            "numero_comprobante": invoice_data.numero_comprobante,
        }
        invoice_data.campos_faltantes = [k for k, v in campos_criticos.items() if not v]
