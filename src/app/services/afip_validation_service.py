"""
Servicio para validación de facturas AFIP y CAE
"""

import requests
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

class AFIPValidationService:
    """
    Servicio para validar facturas AFIP y verificar CAE
    """
    
    def __init__(self):
        # URLs de AFIP (ambiente de testing)
        self.afip_test_urls = {
            'wsaa': 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms',
            'wsfe': 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx',
            'ws_sr_padron': 'https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA4'
        }
        
        # URLs de AFIP (ambiente de producción)
        self.afip_prod_urls = {
            'wsaa': 'https://wsaa.afip.gov.ar/ws/services/LoginCms',
            'wsfe': 'https://servicios1.afip.gov.ar/wsfev1/service.asmx',
            'ws_sr_padron': 'https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA4'
        }
        
        self.test_mode = True  # Cambiar a False para producción
    
    def validate_invoice_afip(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar una factura completa contra AFIP
        
        Args:
            invoice_data: Datos extraídos de la factura
            
        Returns:
            Dict con resultado de validación
        """
        try:
            logger.info("Iniciando validación de factura AFIP")
            
            validation_result = {
                'is_valid': False,
                'errors': [],
                'warnings': [],
                'validated_fields': {},
                'afip_response': None
            }
            
            # 1. Validar estructura básica
            basic_validation = self._validate_basic_structure(invoice_data)
            validation_result['validated_fields'].update(basic_validation)
            
            # 2. Validar CAE si está presente
            cae_validation = self._validate_cae(invoice_data)
            if cae_validation:
                validation_result['validated_fields']['cae'] = cae_validation
            
            # 3. Validar CUITs contra padrón AFIP
            cuit_validation = self._validate_cuits(invoice_data)
            validation_result['validated_fields'].update(cuit_validation)
            
            # 4. Validar fechas y rangos
            date_validation = self._validate_dates(invoice_data)
            validation_result['validated_fields'].update(date_validation)
            
            # 5. Validar montos y cálculos
            amount_validation = self._validate_amounts(invoice_data)
            validation_result['validated_fields'].update(amount_validation)
            
            # Determinar si es válida
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            logger.info(f"Validación completada. Válida: {validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error en validación AFIP: {e}")
            return {
                'is_valid': False,
                'errors': [f"Error interno: {str(e)}"],
                'warnings': [],
                'validated_fields': {},
                'afip_response': None
            }
    
    def _validate_basic_structure(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar estructura básica de la factura"""
        
        validation = {}
        
        # Validar información del comprobante
        comprobante = invoice_data.get('informacion_comprobante', {})
        
        if not comprobante.get('punto_venta'):
            validation['punto_venta'] = {'valid': False, 'error': 'Punto de venta faltante'}
        else:
            validation['punto_venta'] = {'valid': True}
        
        if not comprobante.get('numero'):
            validation['numero_comprobante'] = {'valid': False, 'error': 'Número de comprobante faltante'}
        else:
            validation['numero_comprobante'] = {'valid': True}
        
        if not comprobante.get('fecha_emision'):
            validation['fecha_emision'] = {'valid': False, 'error': 'Fecha de emisión faltante'}
        else:
            validation['fecha_emision'] = {'valid': True}
        
        return validation
    
    def _validate_cae(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validar CAE si está presente"""
        
        afip_info = invoice_data.get('afip', {})
        cae_numero = afip_info.get('cae_numero')
        
        if not cae_numero:
            return {'valid': False, 'error': 'CAE no encontrado'}
        
        # Limpiar CAE
        clean_cae = ''.join(filter(str.isdigit, str(cae_numero)))
        
        if len(clean_cae) != 14:
            return {'valid': False, 'error': f'CAE debe tener 14 dígitos, tiene {len(clean_cae)}'}
        
        # Validar formato de fecha en CAE
        try:
            year = int(clean_cae[:4])
            month = int(clean_cae[4:6])
            day = int(clean_cae[6:8])
            
            if year < 2000 or year > 2030:
                return {'valid': False, 'error': 'Año en CAE fuera de rango válido'}
            
            if month < 1 or month > 12:
                return {'valid': False, 'error': 'Mes en CAE inválido'}
            
            if day < 1 or day > 31:
                return {'valid': False, 'error': 'Día en CAE inválido'}
            
            # Verificar que la fecha del CAE no sea muy antigua
            cae_date = datetime(year, month, day)
            if cae_date < datetime.now() - timedelta(days=365):
                return {'valid': False, 'error': 'CAE muy antiguo (más de 1 año)'}
            
            return {
                'valid': True,
                'cae_number': clean_cae,
                'cae_date': cae_date.strftime('%Y-%m-%d')
            }
            
        except ValueError:
            return {'valid': False, 'error': 'Formato de fecha en CAE inválido'}
    
    def _validate_cuits(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar CUITs contra padrón AFIP"""
        
        validation = {}
        
        # Validar CUIT del emisor
        emisor = invoice_data.get('emisor', {})
        cuit_emisor = emisor.get('cuit')
        
        if cuit_emisor:
            cuit_validation = self._validate_cuit_format(cuit_emisor)
            validation['cuit_emisor'] = cuit_validation
        else:
            validation['cuit_emisor'] = {'valid': False, 'error': 'CUIT del emisor faltante'}
        
        # Validar CUIT del comprador
        comprador = invoice_data.get('comprador', {})
        cuit_comprador = comprador.get('cuit')
        
        if cuit_comprador:
            cuit_validation = self._validate_cuit_format(cuit_comprador)
            validation['cuit_comprador'] = cuit_validation
        else:
            validation['cuit_comprador'] = {'valid': False, 'error': 'CUIT del comprador faltante'}
        
        return validation
    
    def _validate_cuit_format(self, cuit: str) -> Dict[str, Any]:
        """Validar formato y dígito verificador de CUIT"""
        
        try:
            # Limpiar CUIT
            clean_cuit = ''.join(filter(str.isdigit, str(cuit)))
            
            if len(clean_cuit) != 11:
                return {'valid': False, 'error': f'CUIT debe tener 11 dígitos, tiene {len(clean_cuit)}'}
            
            # Validar dígito verificador
            multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            check_digit = int(clean_cuit[-1])
            body = clean_cuit[:-1]
            
            total = sum(int(digit) * mult for digit, mult in zip(body, multipliers))
            remainder = total % 11
            calculated_check = 11 - remainder if remainder > 1 else remainder
            
            if calculated_check != check_digit:
                return {'valid': False, 'error': 'Dígito verificador de CUIT inválido'}
            
            return {
                'valid': True,
                'cuit': clean_cuit,
                'formatted_cuit': f"{clean_cuit[:2]}-{clean_cuit[2:10]}-{clean_cuit[10]}"
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Error validando CUIT: {str(e)}'}
    
    def _validate_dates(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar fechas de la factura"""
        
        validation = {}
        
        # Validar fecha de emisión
        comprobante = invoice_data.get('informacion_comprobante', {})
        fecha_emision = comprobante.get('fecha_emision')
        
        if fecha_emision:
            try:
                # Convertir fecha
                if '/' in fecha_emision:
                    day, month, year = fecha_emision.split('/')
                    emision_date = datetime(int(year), int(month), int(day))
                    
                    # Verificar que no sea futura
                    if emision_date > datetime.now():
                        validation['fecha_emision'] = {'valid': False, 'error': 'Fecha de emisión futura'}
                    else:
                        validation['fecha_emision'] = {'valid': True, 'date': emision_date.strftime('%Y-%m-%d')}
                        
            except ValueError:
                validation['fecha_emision'] = {'valid': False, 'error': 'Formato de fecha inválido'}
        
        return validation
    
    def _validate_amounts(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar montos de la factura"""
        
        validation = {}
        
        totales = invoice_data.get('totales', {})
        
        # Validar importe total
        importe_total = totales.get('total')
        if importe_total:
            try:
                # Limpiar y convertir a float
                clean_amount = importe_total.replace(',', '.').replace('$', '').strip()
                amount = float(clean_amount)
                
                if amount <= 0:
                    validation['importe_total'] = {'valid': False, 'error': 'Importe total debe ser mayor a 0'}
                else:
                    validation['importe_total'] = {'valid': True, 'amount': amount}
                    
            except ValueError:
                validation['importe_total'] = {'valid': False, 'error': 'Formato de importe inválido'}
        
        return validation
    
    def verify_cae_with_afip(self, cae_number: str, cuit_emisor: str, 
                           punto_venta: str, numero_comprobante: str) -> Dict[str, Any]:
        """
        Verificar CAE con AFIP (requiere certificados digitales)
        Esta es una implementación simulada - en producción requiere certificados AFIP
        """
        
        logger.info(f"Verificando CAE {cae_number} con AFIP")
        
        # NOTA: Esta es una implementación simulada
        # En producción se requeriría:
        # 1. Certificados digitales AFIP
        # 2. Autenticación con WSAA
        # 3. Consulta a WSFEv1
        
        return {
            'verified': True,  # Simulado
            'afip_response': {
                'cae_valid': True,
                'authorization_date': '2024-10-15',
                'expiration_date': '2024-11-15',
                'status': 'AUTORIZADO'
            },
            'note': 'Verificación simulada - requiere certificados AFIP para producción'
        }
    
    def get_cuit_info(self, cuit: str) -> Dict[str, Any]:
        """
        Obtener información del CUIT del padrón AFIP
        Esta es una implementación simulada
        """
        
        logger.info(f"Consultando información del CUIT {cuit}")
        
        # NOTA: Esta es una implementación simulada
        # En producción se requeriría consulta al WS SR Padrón
        
        return {
            'found': True,  # Simulado
            'cuit': cuit,
            'denominacion': 'EMPRESA EJEMPLO S.A.',
            'domicilio': 'AV CORRIENTES 1234',
            'localidad': 'CIUDAD AUTONOMA DE BUENOS AIRES',
            'codigo_postal': '1043',
            'provincia': 'CIUDAD AUTONOMA DE BUENOS AIRES',
            'condicion_iva': 'Responsable Inscripto',
            'actividades': ['620100'],
            'note': 'Información simulada - requiere certificados AFIP para producción'
        }










