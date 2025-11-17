"""
Servicio de validación universal para diferentes tipos de documentos
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Tipos de documentos soportados"""
    INVOICE_AFIP = "factura_afip"
    INVOICE_GENERAL = "factura_general"
    RECEIPT = "recibo"
    CONTRACT = "contrato"
    DNI = "dni"
    PASSPORT = "pasaporte"
    CUIL = "cuil"
    CUIT = "cuit"
    BANK_STATEMENT = "extracto_bancario"
    INSURANCE_POLICY = "poliza_seguro"
    MEDICAL_PRESCRIPTION = "receta_medica"
    TAX_RECEIPT = "comprobante_fiscal"
    UNKNOWN = "desconocido"

@dataclass
class ValidationResult:
    """Resultado de validación de un campo"""
    field_name: str
    value: str
    is_valid: bool
    confidence: float
    error_message: Optional[str] = None
    suggestions: List[str] = None

@dataclass
class DocumentValidationResult:
    """Resultado completo de validación de documento"""
    document_type: DocumentType
    is_valid: bool
    overall_confidence: float
    validated_fields: Dict[str, ValidationResult]
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

class UniversalValidationService:
    """
    Servicio de validación universal para diferentes tipos de documentos
    """
    
    def __init__(self):
        # Patrones de validación para diferentes tipos de documentos
        self.validation_patterns = {
            # Documentos argentinos
            'dni': {
                'pattern': r'^\d{7,8}$',
                'min_length': 7,
                'max_length': 8,
                'description': 'DNI argentino (7-8 dígitos)'
            },
            'cuit': {
                'pattern': r'^\d{2}-\d{8}-\d{1}$',
                'min_length': 11,
                'max_length': 11,
                'description': 'CUIT argentino (XX-XXXXXXXX-X)'
            },
            'cuil': {
                'pattern': r'^\d{2}-\d{8}-\d{1}$',
                'min_length': 11,
                'max_length': 11,
                'description': 'CUIL argentino (XX-XXXXXXXX-X)'
            },
            'cae': {
                'pattern': r'^\d{14}$',
                'min_length': 14,
                'max_length': 14,
                'description': 'CAE AFIP (14 dígitos)'
            },
            'invoice_number': {
                'pattern': r'^\d{1,8}$',
                'min_length': 1,
                'max_length': 8,
                'description': 'Número de factura (1-8 dígitos)'
            },
            'point_of_sale': {
                'pattern': r'^\d{4,5}$',
                'min_length': 4,
                'max_length': 5,
                'description': 'Punto de venta (4-5 dígitos)'
            },
            'amount': {
                'pattern': r'^\d{1,3}([.,]\d{3})*([.,]\d{2})?$',
                'min_length': 1,
                'max_length': 15,
                'description': 'Monto en pesos'
            },
            'date_argentina': {
                'pattern': r'^\d{1,2}/\d{1,2}/\d{4}$',
                'min_length': 10,
                'max_length': 10,
                'description': 'Fecha formato argentino (DD/MM/YYYY)'
            },
            'postal_code': {
                'pattern': r'^\d{4}$',
                'min_length': 4,
                'max_length': 4,
                'description': 'Código postal argentino (4 dígitos)'
            },
            'phone_argentina': {
                'pattern': r'^(\+54\s?)?\d{2,4}[\s\-]?\d{6,8}$',
                'min_length': 8,
                'max_length': 15,
                'description': 'Teléfono argentino'
            },
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'min_length': 5,
                'max_length': 100,
                'description': 'Email válido'
            },
            'passport': {
                'pattern': r'^[A-Z]{2}\d{6,7}$',
                'min_length': 8,
                'max_length': 9,
                'description': 'Pasaporte (2 letras + 6-7 dígitos)'
            }
        }
        
        # Configuración de validación por tipo de documento
        self.document_configs = {
            DocumentType.INVOICE_AFIP: {
                'required_fields': ['punto_venta', 'numero_comprobante', 'fecha_emision', 'cuit_emisor', 'importe_total'],
                'optional_fields': ['cae_numero', 'cuit_comprador', 'razon_social_emisor', 'razon_social_comprador'],
                'validators': {
                    'punto_venta': 'point_of_sale',
                    'numero_comprobante': 'invoice_number',
                    'fecha_emision': 'date_argentina',
                    'cuit_emisor': 'cuit',
                    'cuit_comprador': 'cuit',
                    'importe_total': 'amount',
                    'cae_numero': 'cae'
                }
            },
            DocumentType.RECEIPT: {
                'required_fields': ['numero_recibo', 'fecha', 'monto', 'emisor'],
                'optional_fields': ['cuit_emisor', 'descripcion', 'metodo_pago'],
                'validators': {
                    'numero_recibo': 'invoice_number',
                    'fecha': 'date_argentina',
                    'monto': 'amount',
                    'cuit_emisor': 'cuit'
                }
            },
            DocumentType.DNI: {
                'required_fields': ['numero_dni', 'apellido', 'nombre'],
                'optional_fields': ['fecha_nacimiento', 'domicilio', 'sexo', 'nacionalidad'],
                'validators': {
                    'numero_dni': 'dni',
                    'fecha_nacimiento': 'date_argentina'
                }
            },
            DocumentType.CONTRACT: {
                'required_fields': ['numero_contrato', 'fecha_inicio', 'partes_contrato'],
                'optional_fields': ['fecha_fin', 'monto', 'descripcion'],
                'validators': {
                    'numero_contrato': 'invoice_number',
                    'fecha_inicio': 'date_argentina',
                    'fecha_fin': 'date_argentina',
                    'monto': 'amount'
                }
            },
            DocumentType.PASSPORT: {
                'required_fields': ['numero_pasaporte', 'apellido', 'nombre', 'nacionalidad'],
                'optional_fields': ['fecha_nacimiento', 'fecha_emision', 'fecha_vencimiento'],
                'validators': {
                    'numero_pasaporte': 'passport',
                    'fecha_nacimiento': 'date_argentina',
                    'fecha_emision': 'date_argentina',
                    'fecha_vencimiento': 'date_argentina'
                }
            }
        }
    
    def validate_document(self, extracted_data: Dict[str, Any]) -> DocumentValidationResult:
        """
        Validar documento completo basado en su tipo
        
        Args:
            extracted_data: Datos extraídos del documento
            
        Returns:
            DocumentValidationResult: Resultado completo de validación
        """
        try:
            logger.info("Iniciando validación universal de documento")
            
            # Detectar tipo de documento
            document_type = self._detect_document_type(extracted_data)
            logger.info(f"Tipo de documento detectado: {document_type.value}")
            
            # Obtener configuración de validación
            config = self.document_configs.get(document_type, {})
            
            # Validar campos
            validated_fields = {}
            errors = []
            warnings = []
            recommendations = []
            
            # Validar campos requeridos
            required_fields = config.get('required_fields', [])
            for field in required_fields:
                field_data = self._get_field_data(extracted_data, field)
                validation_result = self._validate_field(field, field_data, config.get('validators', {}))
                validated_fields[field] = validation_result
                
                if not validation_result.is_valid:
                    errors.append(f"Campo requerido '{field}' no válido: {validation_result.error_message}")
                elif validation_result.confidence < 0.7:
                    warnings.append(f"Campo '{field}' tiene baja confianza: {validation_result.confidence:.2f}")
            
            # Validar campos opcionales
            optional_fields = config.get('optional_fields', [])
            for field in optional_fields:
                field_data = self._get_field_data(extracted_data, field)
                if field_data:  # Solo validar si el campo existe
                    validation_result = self._validate_field(field, field_data, config.get('validators', {}))
                    validated_fields[field] = validation_result
                    
                    if not validation_result.is_valid:
                        warnings.append(f"Campo opcional '{field}' no válido: {validation_result.error_message}")
            
            # Validaciones específicas por tipo de documento
            type_specific_validation = self._validate_type_specific_rules(document_type, extracted_data)
            errors.extend(type_specific_validation.get('errors', []))
            warnings.extend(type_specific_validation.get('warnings', []))
            recommendations.extend(type_specific_validation.get('recommendations', []))
            
            # Calcular confianza general
            overall_confidence = self._calculate_overall_confidence(validated_fields)
            
            # Determinar si el documento es válido
            is_valid = len(errors) == 0 and overall_confidence > 0.6
            
            # Generar recomendaciones
            if not is_valid:
                recommendations.append("Revisar campos marcados como inválidos")
            if overall_confidence < 0.8:
                recommendations.append("Considerar revisar la calidad del documento original")
            
            result = DocumentValidationResult(
                document_type=document_type,
                is_valid=is_valid,
                overall_confidence=overall_confidence,
                validated_fields=validated_fields,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations
            )
            
            logger.info(f"Validación completada. Válido: {is_valid}, Confianza: {overall_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error en validación universal: {e}")
            return DocumentValidationResult(
                document_type=DocumentType.UNKNOWN,
                is_valid=False,
                overall_confidence=0.0,
                validated_fields={},
                errors=[f"Error interno: {str(e)}"],
                warnings=[],
                recommendations=[]
            )
    
    def _detect_document_type(self, extracted_data: Dict[str, Any]) -> DocumentType:
        """Detectar tipo de documento basado en datos extraídos"""
        
        # Verificar indicadores específicos
        tipo_documento = extracted_data.get('tipo_documento', '').lower()
        
        if tipo_documento == 'factura_afip' or 'afip' in tipo_documento:
            return DocumentType.INVOICE_AFIP
        elif 'factura' in tipo_documento or 'invoice' in tipo_documento:
            return DocumentType.INVOICE_GENERAL
        elif 'recibo' in tipo_documento or 'receipt' in tipo_documento:
            return DocumentType.RECEIPT
        elif 'contrato' in tipo_documento or 'contract' in tipo_documento:
            return DocumentType.CONTRACT
        elif 'dni' in tipo_documento:
            return DocumentType.DNI
        elif 'pasaporte' in tipo_documento or 'passport' in tipo_documento:
            return DocumentType.PASSPORT
        
        # Detectar por campos presentes
        if extracted_data.get('afip', {}).get('cae_numero'):
            return DocumentType.INVOICE_AFIP
        elif extracted_data.get('numero_dni'):
            return DocumentType.DNI
        elif extracted_data.get('numero_pasaporte'):
            return DocumentType.PASSPORT
        elif extracted_data.get('numero_recibo'):
            return DocumentType.RECEIPT
        elif extracted_data.get('numero_contrato'):
            return DocumentType.CONTRACT
        
        # Detectar por estructura
        if extracted_data.get('emisor') and extracted_data.get('comprador'):
            return DocumentType.INVOICE_GENERAL
        elif extracted_data.get('apellido') and extracted_data.get('nombre'):
            return DocumentType.DNI
        
        return DocumentType.UNKNOWN
    
    def _get_field_data(self, extracted_data: Dict[str, Any], field_name: str) -> Optional[str]:
        """Obtener datos de un campo específico desde los datos extraídos"""
        
        # Mapeo de campos a ubicaciones en los datos
        field_mapping = {
            'punto_venta': ['informacion_comprobante', 'punto_venta'],
            'numero_comprobante': ['informacion_comprobante', 'numero'],
            'fecha_emision': ['informacion_comprobante', 'fecha_emision'],
            'cuit_emisor': ['emisor', 'cuit'],
            'cuit_comprador': ['comprador', 'cuit'],
            'razon_social_emisor': ['emisor', 'razon_social'],
            'razon_social_comprador': ['comprador', 'razon_social'],
            'importe_total': ['totales', 'total'],
            'cae_numero': ['afip', 'cae_numero'],
            'numero_dni': ['numero_dni'],
            'apellido': ['apellido'],
            'nombre': ['nombre'],
            'fecha_nacimiento': ['fecha_nacimiento'],
            'numero_pasaporte': ['numero_pasaporte'],
            'nacionalidad': ['nacionalidad'],
            'numero_recibo': ['numero_recibo'],
            'monto': ['monto'],
            'emisor': ['emisor'],
            'numero_contrato': ['numero_contrato'],
            'fecha_inicio': ['fecha_inicio'],
            'partes_contrato': ['partes_contrato']
        }
        
        path = field_mapping.get(field_name, [field_name])
        
        # Navegar por el path
        data = extracted_data
        for key in path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        
        return str(data) if data else None
    
    def _validate_field(self, field_name: str, field_value: str, validators: Dict[str, str]) -> ValidationResult:
        """Validar un campo específico"""
        
        if not field_value:
            return ValidationResult(
                field_name=field_name,
                value="",
                is_valid=False,
                confidence=0.0,
                error_message="Campo vacío"
            )
        
        # Obtener tipo de validador
        validator_type = validators.get(field_name)
        
        if not validator_type:
            # Validación genérica
            return ValidationResult(
                field_name=field_name,
                value=field_value,
                is_valid=True,
                confidence=0.8,
                error_message=None
            )
        
        # Obtener patrón de validación
        pattern_config = self.validation_patterns.get(validator_type)
        
        if not pattern_config:
            return ValidationResult(
                field_name=field_name,
                value=field_value,
                is_valid=False,
                confidence=0.0,
                error_message=f"Validador '{validator_type}' no encontrado"
            )
        
        # Validar patrón
        pattern = pattern_config['pattern']
        min_length = pattern_config['min_length']
        max_length = pattern_config['max_length']
        
        is_valid = True
        confidence = 0.8
        error_message = None
        suggestions = []
        
        # Validar longitud
        if len(field_value) < min_length or len(field_value) > max_length:
            is_valid = False
            error_message = f"Longitud incorrecta. Esperado: {min_length}-{max_length}, obtenido: {len(field_value)}"
            confidence = 0.2
        
        # Validar patrón
        elif not re.match(pattern, field_value):
            is_valid = False
            error_message = f"No coincide con el patrón esperado: {pattern_config['description']}"
            confidence = 0.3
            
            # Sugerir correcciones
            suggestions = self._suggest_corrections(field_value, validator_type)
        
        # Validaciones específicas
        if validator_type == 'cuit' or validator_type == 'cuil':
            if not self._validate_cuit_cuil(field_value):
                is_valid = False
                error_message = "Dígito verificador inválido"
                confidence = 0.1
        elif validator_type == 'cae':
            if not self._validate_cae_format(field_value):
                is_valid = False
                error_message = "Formato de CAE inválido"
                confidence = 0.1
        elif validator_type == 'date_argentina':
            if not self._validate_date_format(field_value):
                is_valid = False
                error_message = "Formato de fecha inválido"
                confidence = 0.1
        
        return ValidationResult(
            field_name=field_name,
            value=field_value,
            is_valid=is_valid,
            confidence=confidence,
            error_message=error_message,
            suggestions=suggestions
        )
    
    def _validate_cuit_cuil(self, cuit: str) -> bool:
        """Validar dígito verificador de CUIT/CUIL"""
        try:
            clean_cuit = re.sub(r'[^\d]', '', cuit)
            if len(clean_cuit) != 11:
                return False
            
            multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            check_digit = int(clean_cuit[-1])
            body = clean_cuit[:-1]
            
            total = sum(int(digit) * mult for digit, mult in zip(body, multipliers))
            remainder = total % 11
            calculated_check = 11 - remainder if remainder > 1 else remainder
            
            return calculated_check == check_digit
        except:
            return False
    
    def _validate_cae_format(self, cae: str) -> bool:
        """Validar formato de CAE"""
        try:
            if len(cae) != 14 or not cae.isdigit():
                return False
            
            # Validar fecha en CAE
            year = int(cae[:4])
            month = int(cae[4:6])
            day = int(cae[6:8])
            
            if year < 2000 or year > 2030:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            
            return True
        except:
            return False
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validar formato de fecha argentina"""
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    def _suggest_corrections(self, value: str, validator_type: str) -> List[str]:
        """Sugerir correcciones para valores inválidos"""
        suggestions = []
        
        if validator_type == 'cuit' or validator_type == 'cuil':
            # Limpiar formato
            clean_value = re.sub(r'[^\d]', '', value)
            if len(clean_value) == 11:
                formatted = f"{clean_value[:2]}-{clean_value[2:10]}-{clean_value[10]}"
                suggestions.append(f"Formato sugerido: {formatted}")
        elif validator_type == 'dni':
            if len(value) < 7:
                suggestions.append("DNI debe tener al menos 7 dígitos")
            elif len(value) > 8:
                suggestions.append("DNI debe tener máximo 8 dígitos")
        elif validator_type == 'date_argentina':
            suggestions.append("Formato sugerido: DD/MM/YYYY")
        
        return suggestions
    
    def _validate_type_specific_rules(self, document_type: DocumentType, extracted_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validar reglas específicas por tipo de documento"""
        
        errors = []
        warnings = []
        recommendations = []
        
        if document_type == DocumentType.INVOICE_AFIP:
            # Validar coherencia entre fecha de emisión y CAE
            fecha_emision = self._get_field_data(extracted_data, 'fecha_emision')
            cae_numero = self._get_field_data(extracted_data, 'cae_numero')
            
            if fecha_emision and cae_numero:
                try:
                    emision_date = datetime.strptime(fecha_emision, '%d/%m/%Y')
                    cae_year = int(cae_numero[:4])
                    cae_month = int(cae_numero[4:6])
                    cae_day = int(cae_numero[6:8])
                    cae_date = datetime(cae_year, cae_month, cae_day)
                    
                    # CAE debe ser posterior o igual a la fecha de emisión
                    if cae_date < emision_date:
                        warnings.append("CAE anterior a fecha de emisión")
                except:
                    warnings.append("No se pudo validar coherencia entre fecha de emisión y CAE")
        
        elif document_type == DocumentType.DNI:
            # Validar que nombre y apellido no sean iguales
            nombre = self._get_field_data(extracted_data, 'nombre')
            apellido = self._get_field_data(extracted_data, 'apellido')
            
            if nombre and apellido and nombre.lower() == apellido.lower():
                warnings.append("Nombre y apellido son iguales")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _calculate_overall_confidence(self, validated_fields: Dict[str, ValidationResult]) -> float:
        """Calcular confianza general del documento"""
        
        if not validated_fields:
            return 0.0
        
        total_confidence = sum(field.confidence for field in validated_fields.values())
        return total_confidence / len(validated_fields)







