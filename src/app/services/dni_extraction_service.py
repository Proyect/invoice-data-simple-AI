"""
Servicio de Extracción para Documentos Nacionales de Identidad (DNI) Argentinos
==============================================================================

Servicio especializado para extraer datos de DNI argentinos, incluyendo:
- DNI tradicional (libreta cívica)
- DNI tarjeta (nuevo formato)
- DNI digital
- Pasaporte argentino
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DNIData:
    """Datos extraídos de un DNI argentino"""
    tipo_documento: str
    numero_dni: Optional[str] = None
    apellido: Optional[str] = None
    nombre: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    fecha_emision: Optional[str] = None
    fecha_vencimiento: Optional[str] = None
    lugar_emision: Optional[str] = None
    numero_tramite: Optional[str] = None
    codigo_verificacion: Optional[str] = None
    domicilio: Optional[str] = None
    estado_civil: Optional[str] = None
    profesion: Optional[str] = None
    foto_path: Optional[str] = None
    huella_dactilar: Optional[str] = None

class DNIExtractionService:
    """Servicio especializado para extraer datos de DNI argentinos"""
    
    def __init__(self):
        # Patrones específicos para DNI argentino
        self.dni_patterns = {
            "numero_dni": [
                r"DNI\s*:?\s*(\d{7,8})",
                r"(\d{7,8})\s*DNI",
                r"Documento\s*:?\s*(\d{7,8})",
                r"(\d{7,8})\s*Documento",
                r"N[º°]?\s*:?\s*(\d{7,8})",
                r"(\d{7,8})\s*N[º°]?",
            ],
            "apellido": [
                r"Apellido\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"Surname\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Apellido",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Surname",
            ],
            "nombre": [
                r"Nombre\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"Name\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Nombre",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Name",
                r"Nombres\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
            ],
            "sexo": [
                r"Sexo\s*:?\s*([MF])",
                r"Gender\s*:?\s*([MF])",
                r"([MF])\s*Sexo",
                r"([MF])\s*Gender",
                r"MASCULINO|FEMENINO",
            ],
            "fecha_nacimiento": [
                r"Fecha\s+de\s+Nacimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Birth\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Nacimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*Nacimiento",
                r"(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
            ],
            "lugar_nacimiento": [
                r"Lugar\s+de\s+Nacimiento\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"Birth\s+Place\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"Nacido\s+en\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"([A-ZÁÉÍÓÚÑ\s,\.]+)\s*Nacimiento",
            ],
            "nacionalidad": [
                r"Nacionalidad\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"Nationality\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Nacionalidad",
                r"ARGENTINO|ARGENTINA",
            ],
            "fecha_emision": [
                r"Fecha\s+de\s+Emisión\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Issue\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Emisión\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*Emisión",
            ],
            "fecha_vencimiento": [
                r"Fecha\s+de\s+Vencimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Expiry\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Vencimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"Válido\s+hasta\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ],
            "lugar_emision": [
                r"Lugar\s+de\s+Emisión\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"Issue\s+Place\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"Emitido\s+en\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"([A-ZÁÉÍÓÚÑ\s,\.]+)\s*Emisión",
            ],
            "numero_tramite": [
                r"N[º°]?\s+de\s+Trámite\s*:?\s*([A-Z0-9\-]+)",
                r"Trámite\s*:?\s*([A-Z0-9\-]+)",
                r"Tramite\s*:?\s*([A-Z0-9\-]+)",
                r"([A-Z0-9\-]+)\s*Trámite",
            ],
            "codigo_verificacion": [
                r"Código\s+de\s+Verificación\s*:?\s*([A-Z0-9]+)",
                r"Verification\s+Code\s*:?\s*([A-Z0-9]+)",
                r"Código\s*:?\s*([A-Z0-9]+)",
                r"Code\s*:?\s*([A-Z0-9]+)",
            ],
            "domicilio": [
                r"Domicilio\s*:?\s*([A-ZÁÉÍÓÚÑ0-9\s,\.\-]+)",
                r"Address\s*:?\s*([A-ZÁÉÍÓÚÑ0-9\s,\.\-]+)",
                r"Residencia\s*:?\s*([A-ZÁÉÍÓÚÑ0-9\s,\.\-]+)",
                r"([A-ZÁÉÍÓÚÑ0-9\s,\.\-]+)\s*Domicilio",
            ],
            "estado_civil": [
                r"Estado\s+Civil\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"Marital\s+Status\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"([A-ZÁÉÍÓÚÑ\s]+)\s*Estado\s+Civil",
                r"SOLTERO|SOLTERA|CASADO|CASADA|DIVORCIADO|DIVORCIADA|VIUDO|VIUDA",
            ],
            "profesion": [
                r"Profesión\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"Occupation\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
                r"([A-ZÁÉÍÓÚÑ\s,\.]+)\s*Profesión",
                r"([A-ZÁÉÍÓÚÑ\s,\.]+)\s*Occupation",
            ]
        }
        
        # Patrones para detectar tipo de DNI
        self.dni_type_patterns = {
            "dni_tarjeta": [
                r"REPÚBLICA\s+ARGENTINA",
                r"DOCUMENTO\s+NACIONAL\s+DE\s+IDENTIDAD",
                r"DNI\s+TARJETA",
                r"TARJETA\s+DE\s+IDENTIDAD"
            ],
            "dni_libreta": [
                r"LIBRETA\s+CÍVICA",
                r"LIBRETA\s+CIVICA",
                r"LC\s*:?\s*\d{7,8}",
                r"CÍVICA\s*:?\s*\d{7,8}"
            ],
            "pasaporte": [
                r"PASAPORTE",
                r"PASSPORT",
                r"REPÚBLICA\s+ARGENTINA\s+PASAPORTE",
                r"PASAPORTE\s+ARGENTINO"
            ]
        }
    
    def extract_dni_data(self, text: str) -> DNIData:
        """Extraer datos de un DNI argentino"""
        try:
            # Detectar tipo de documento
            document_type = self._detect_dni_type(text)
            
            data = DNIData(tipo_documento=document_type)
            
            # Extraer datos usando patrones
            data.numero_dni = self._extract_field(text, self.dni_patterns["numero_dni"])
            data.apellido = self._extract_field(text, self.dni_patterns["apellido"])
            data.nombre = self._extract_field(text, self.dni_patterns["nombre"])
            data.sexo = self._extract_field(text, self.dni_patterns["sexo"])
            data.fecha_nacimiento = self._extract_field(text, self.dni_patterns["fecha_nacimiento"])
            data.lugar_nacimiento = self._extract_field(text, self.dni_patterns["lugar_nacimiento"])
            data.nacionalidad = self._extract_field(text, self.dni_patterns["nacionalidad"])
            data.fecha_emision = self._extract_field(text, self.dni_patterns["fecha_emision"])
            data.fecha_vencimiento = self._extract_field(text, self.dni_patterns["fecha_vencimiento"])
            data.lugar_emision = self._extract_field(text, self.dni_patterns["lugar_emision"])
            data.numero_tramite = self._extract_field(text, self.dni_patterns["numero_tramite"])
            data.codigo_verificacion = self._extract_field(text, self.dni_patterns["codigo_verificacion"])
            data.domicilio = self._extract_field(text, self.dni_patterns["domicilio"])
            data.estado_civil = self._extract_field(text, self.dni_patterns["estado_civil"])
            data.profesion = self._extract_field(text, self.dni_patterns["profesion"])
            
            # Post-procesar datos
            data = self._post_process_dni_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de DNI: {e}")
            return DNIData(tipo_documento="dni")
    
    def _detect_dni_type(self, text: str) -> str:
        """Detectar tipo de DNI"""
        text_upper = text.upper()
        
        for dni_type, patterns in self.dni_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    return dni_type
        
        # Si no se detecta tipo específico, asumir DNI tarjeta
        return "dni_tarjeta"
    
    def _extract_field(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extraer un campo usando múltiples patrones"""
        best_match = None
        best_score = 0
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.groups():
                    result = match.group(1).strip()
                else:
                    result = match.group(0).strip()
                
                # Limpiar resultado
                result = re.sub(r'\s+', ' ', result)
                result = result.strip('.,:;')
                
                # Validar resultado
                if self._validate_dni_field(result, pattern):
                    score = self._calculate_dni_field_score(result, pattern)
                    if score > best_score:
                        best_score = score
                        best_match = result
        
        return best_match if best_match and len(best_match) > 1 else None
    
    def _validate_dni_field(self, field: str, pattern: str) -> bool:
        """Validar campo extraído de DNI"""
        if not field or len(field) < 1:
            return False
        
        # Validaciones específicas por tipo de campo
        if "numero_dni" in pattern:
            return re.match(r'^\d{7,8}$', field)
        elif "sexo" in pattern:
            return field.upper() in ['M', 'F', 'MASCULINO', 'FEMENINO']
        elif "fecha" in pattern:
            return self._is_valid_date(field)
        elif "apellido" in pattern or "nombre" in pattern:
            return re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', field) and len(field) >= 2
        
        return True
    
    def _calculate_dni_field_score(self, field: str, pattern: str) -> float:
        """Calcular score de calidad para campo de DNI"""
        score = 0.0
        
        # Bonus por longitud apropiada
        if 2 <= len(field) <= 50:
            score += 1.0
        
        # Bonus por patrones específicos
        if "numero_dni" in pattern and re.match(r'^\d{7,8}$', field):
            score += 2.0
        elif "sexo" in pattern and field.upper() in ['M', 'F']:
            score += 2.0
        elif "fecha" in pattern and self._is_valid_date(field):
            score += 1.5
        elif "apellido" in pattern and re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', field):
            score += 1.0
        
        return score
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validar formato de fecha"""
        date_patterns = [
            r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$',
            r'^\d{1,2}\s+de\s+\w+\s+de\s+\d{4}$'
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, date_str):
                return True
        
        return False
    
    def _post_process_dni_data(self, data: DNIData) -> DNIData:
        """Post-procesar datos de DNI"""
        # Limpiar nombres
        if data.apellido:
            data.apellido = self._clean_name(data.apellido)
        if data.nombre:
            data.nombre = self._clean_name(data.nombre)
        
        # Formatear fechas
        if data.fecha_nacimiento:
            data.fecha_nacimiento = self._format_date(data.fecha_nacimiento)
        if data.fecha_emision:
            data.fecha_emision = self._format_date(data.fecha_emision)
        if data.fecha_vencimiento:
            data.fecha_vencimiento = self._format_date(data.fecha_vencimiento)
        
        # Limpiar sexo
        if data.sexo:
            data.sexo = self._clean_sexo(data.sexo)
        
        # Limpiar nacionalidad
        if data.nacionalidad:
            data.nacionalidad = self._clean_nacionalidad(data.nacionalidad)
        
        return data
    
    def _clean_name(self, name: str) -> str:
        """Limpiar nombre o apellido"""
        # Remover caracteres especiales excepto espacios
        name = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', name)
        # Normalizar espacios
        name = re.sub(r'\s+', ' ', name)
        return name.strip()
    
    def _format_date(self, date: str) -> str:
        """Formatear fecha a DD/MM/YYYY"""
        # Formato DD/MM/YYYY o DD-MM-YYYY
        if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', date):
            parts = re.split(r'[/-]', date)
            day, month, year = parts[0], parts[1], parts[2]
            if len(year) == 2:
                year = '20' + year
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Formato DD de mes de YYYY
        if re.match(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', date):
            match = re.match(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date)
            if match:
                day, month_name, year = match.groups()
                month_map = {
                    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                }
                month = month_map.get(month_name.lower(), '01')
                return f"{day.zfill(2)}/{month}/{year}"
        
        return date
    
    def _clean_sexo(self, sexo: str) -> str:
        """Limpiar campo de sexo"""
        sexo = sexo.upper().strip()
        if sexo in ['M', 'MASCULINO']:
            return 'M'
        elif sexo in ['F', 'FEMENINO']:
            return 'F'
        return sexo
    
    def _clean_nacionalidad(self, nacionalidad: str) -> str:
        """Limpiar nacionalidad"""
        nacionalidad = nacionalidad.upper().strip()
        if 'ARGENTINO' in nacionalidad or 'ARGENTINA' in nacionalidad:
            return 'ARGENTINO'
        return nacionalidad
    
    def validate_dni_number(self, dni: str) -> bool:
        """Validar número de DNI argentino"""
        if not dni or not re.match(r'^\d{7,8}$', dni):
            return False
        
        # Validación básica de rango
        dni_num = int(dni)
        return 1000000 <= dni_num <= 99999999

# Instancia global del servicio
_dni_extraction_service = None

def get_dni_extraction_service() -> DNIExtractionService:
    """Obtener instancia del servicio de extracción de DNI"""
    global _dni_extraction_service
    if _dni_extraction_service is None:
        _dni_extraction_service = DNIExtractionService()
    return _dni_extraction_service
