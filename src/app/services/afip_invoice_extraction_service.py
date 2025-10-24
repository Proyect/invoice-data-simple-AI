"""
Servicio especializado para extracción de datos de facturas AFIP/ARCA
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AFIPInvoiceData:
    """Estructura de datos para facturas AFIP"""
    # Información del comprobante
    tipo_comprobante: str = ""
    punto_venta: str = ""
    numero_comprobante: str = ""
    fecha_emision: str = ""
    fecha_vencimiento: str = ""
    
    # Información del emisor
    razon_social_emisor: str = ""
    domicilio_comercial: str = ""
    cuit_emisor: str = ""
    condicion_iva_emisor: str = ""
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
    
    # Totales
    subtotal: str = ""
    importe_otros_tributos: str = ""
    importe_total: str = ""
    
    # Información AFIP
    cae_numero: str = ""
    fecha_vencimiento_cae: str = ""
    pagina_actual: str = ""
    total_paginas: str = ""
    
    def __post_init__(self):
        if self.productos is None:
            self.productos = []

class AFIPInvoiceExtractionService:
    """
    Servicio especializado para extraer datos de facturas AFIP/ARCA
    """
    
    def __init__(self):
        # Importar servicios
        from .afip_validation_service import AFIPValidationService
        from .specialized_ocr_service import SpecializedOCRService
        from .universal_validation_service import UniversalValidationService
        
        self.validation_service = AFIPValidationService()
        self.specialized_ocr = SpecializedOCRService()
        self.universal_validation = UniversalValidationService()
        
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
        
        # Tipos de comprobante AFIP
        self.tipos_comprobante = {
            'C': 'Factura C',
            'A': 'Factura A',
            'B': 'Factura B',
            'E': 'Factura E',
        }
    
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
            
            # Extraer totales
            self._extract_totales(text, invoice_data)
            
            # Extraer información AFIP
            self._extract_afip_info(text, invoice_data)
            
            # Si tenemos imagen, usar OCR especializado para campos críticos
            if image_path:
                self._enhance_with_specialized_ocr(image_path, invoice_data)
            
            # Convertir a diccionario
            result = self._to_dict(invoice_data)
            
            logger.info(f"Datos AFIP extraídos: {len(result)} campos")
            return result
            
        except Exception as e:
            logger.error(f"Error extrayendo datos AFIP: {e}")
            return {}
    
    def _extract_comprobante_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información del comprobante con múltiples patrones"""
        
        # Tipo de comprobante (buscar letra en código)
        tipo_match = re.search(r'COD\.?\s*(\w+)', text)
        if tipo_match:
            codigo = tipo_match.group(1)
            invoice_data.tipo_comprobante = self.tipos_comprobante.get(codigo, f"Comprobante {codigo}")
        
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
        """Validar formato y dígito verificador de CUIT"""
        try:
            # Limpiar formato
            clean_cuit = re.sub(r'[^\d]', '', cuit)
            
            if len(clean_cuit) != 11:
                return False
            
            # Validar dígito verificador
            multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            check_digit = int(clean_cuit[-1])
            body = clean_cuit[:-1]
            
            total = sum(int(digit) * mult for digit, mult in zip(body, multipliers))
            remainder = total % 11
            calculated_check = 11 - remainder if remainder > 1 else remainder
            
            return calculated_check == check_digit
            
        except Exception:
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
        """Validar formato del CAE"""
        try:
            # CAE debe tener exactamente 14 dígitos
            if len(cae) != 14:
                return False
            
            # Debe ser numérico
            if not cae.isdigit():
                return False
            
            # Validar rango de fechas (los primeros dígitos indican fecha)
            # CAE tiene formato: AAAAMMDDHHMMSS (año, mes, día, hora, min, seg, miliseg)
            year = int(cae[:4])
            month = int(cae[4:6])
            day = int(cae[6:8])
            
            # Validar año (debe estar en rango razonable)
            if year < 2000 or year > 2030:
                return False
            
            # Validar mes
            if month < 1 or month > 12:
                return False
            
            # Validar día
            if day < 1 or day > 31:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_emisor_info(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer información del emisor con múltiples patrones"""
        
        # Razón social del emisor
        invoice_data.razon_social_emisor = self._extract_with_multiple_patterns(text, 'razon_social_emisor')
        
        # Domicilio comercial
        invoice_data.domicilio_comercial = self._extract_with_multiple_patterns(text, 'domicilio_comercial')
        
        # Condición frente al IVA del emisor
        invoice_data.condicion_iva_emisor = self._extract_with_multiple_patterns(text, 'condicion_iva_emisor')
        
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
        """Extraer información de productos/servicios"""
        
        # Buscar tabla de productos
        # Patrón para encontrar líneas de productos
        producto_pattern = r'(\w+)\s+([^\n\r]+?)\s+(\d+,\d+)\s+(\w+)\s+([\d,\.]+)\s+(\d+,\d+)\s+([\d,\.]+)\s+([\d,\.]+)'
        
        matches = re.findall(producto_pattern, text)
        
        for match in matches:
            producto = {
                'codigo': match[0],
                'descripcion': match[1].strip(),
                'cantidad': match[2],
                'unidad_medida': match[3],
                'precio_unitario': match[4],
                'porcentaje_bonificacion': match[5],
                'importe_bonificacion': match[6],
                'subtotal': match[7]
            }
            invoice_data.productos.append(producto)
    
    def _extract_totales(self, text: str, invoice_data: AFIPInvoiceData):
        """Extraer totales con múltiples patrones"""
        
        # Subtotal
        invoice_data.subtotal = self._extract_with_multiple_patterns(text, 'subtotal')
        
        # Importe otros tributos
        invoice_data.importe_otros_tributos = self._extract_with_multiple_patterns(text, 'importe_otros_tributos')
        
        # Importe total
        invoice_data.importe_total = self._extract_with_multiple_patterns(text, 'importe_total')
    
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
                'domicilio': invoice_data.domicilio_comercial,
                'cuit': invoice_data.cuit_emisor,
                'condicion_iva': invoice_data.condicion_iva_emisor,
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
            'totales': {
                'subtotal': invoice_data.subtotal,
                'otros_tributos': invoice_data.importe_otros_tributos,
                'total': invoice_data.importe_total,
            },
            'afip': {
                'cae_numero': invoice_data.cae_numero,
                'cae_vencimiento': invoice_data.fecha_vencimiento_cae,
                'pagina_actual': invoice_data.pagina_actual,
                'total_paginas': invoice_data.total_paginas,
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
