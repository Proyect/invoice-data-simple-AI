"""
Servicio de Extracción para Documentos Académicos
================================================

Servicio especializado para extraer datos de títulos, certificados, diplomas y licencias.
Incluye patrones específicos para documentos académicos argentinos e internacionales.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AcademicDocumentData:
    """Datos extraídos de documentos académicos"""
    tipo_documento: str
    institucion: Optional[str] = None
    titulo_otorgado: Optional[str] = None
    nombre_estudiante: Optional[str] = None
    numero_documento: Optional[str] = None
    fecha_emision: Optional[str] = None
    fecha_vencimiento: Optional[str] = None
    duracion: Optional[str] = None
    modalidad: Optional[str] = None
    calificacion: Optional[str] = None
    promedio: Optional[str] = None
    director_tesis: Optional[str] = None
    jurado: Optional[List[str]] = None
    numero_registro: Optional[str] = None
    codigo_verificacion: Optional[str] = None
    nivel_academico: Optional[str] = None
    area_estudio: Optional[str] = None
    creditos: Optional[str] = None
    horas_cursadas: Optional[str] = None
    sede: Optional[str] = None
    facultad: Optional[str] = None
    carrera: Optional[str] = None
    resolucion: Optional[str] = None
    validez_nacional: Optional[str] = None
    equivalencia: Optional[str] = None

class AcademicDocumentExtractionService:
    """Servicio especializado para extraer datos de títulos y certificados"""
    
    def __init__(self):
        # Patrones específicos para títulos académicos
        self.titulo_patterns = {
            "institucion": [
                r"^([A-ZÁÉÍÓÚÑ\s\.]{5,50})\s+(?:universidad|instituto|colegio|escuela|university|institute|college|school)",
                r"(?:universidad|instituto|colegio|escuela|university|institute|college|school)\s+([A-ZÁÉÍÓÚÑ\s\.]{5,50})",
                r"^([A-ZÁÉÍÓÚÑ\s\.]{5,50})\s+(?:de|del|of|of the)",
            ],
            "titulo": [
                r"(?:título|degree|diploma|certificado|title)\s+(?:de|en|in|of)\s+([A-ZÁÉÍÓÚÑ\s\.]{2,50})",
                r"(?:bachiller|licenciado|ingeniero|doctor|magister|master|especialista|bachelor|engineer|specialist)\s+(?:en|in|de|of)\s+([A-ZÁÉÍÓÚÑ\s\.]{2,50})",
                r"(?:bachelor|master|doctor|engineer|specialist)\s+(?:of|in|en)\s+([A-ZÁÉÍÓÚÑ\s\.]{2,50})",
                r"(?:carrera|career|programa|program)\s+(?:de|en|in|of)\s+([A-ZÁÉÍÓÚÑ\s\.]{2,50})",
            ],
            "estudiante": [
                r"(?:estudiante|alumno|student|graduate|egresado)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?:\s+DNI|\s*$)",
                r"(?:nombre|name|apellido|surname)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?:\s+DNI|\s*$)",
                r"([A-ZÁÉÍÓÚÑ\s\.]{3,50})\s+(?:estudiante|alumno|student|egresado)",
                r"(?:señor|señora|sr\.|sra\.|mr\.|mrs\.|ms\.)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?:\s+DNI|\s*$)",
                r"(?:se otorga|se certifica|se confiere)\s+(?:a|al|a la)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?:\s+DNI|\s*$)",
            ],
            "fecha_emision": [
                r"(?:fecha|date|issued|emisión|otorgado|granted)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?:fecha|date|issued|emisión|otorgado|granted)\s*:?\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
                r"(?:el|on)\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
            ],
            "numero_registro": [
                r"(?:registro|record|número|number|nro|nº|#)\s*:?\s*([A-Z0-9\-\.]{3,20})",
                r"(?:código|code|cod\.)\s*:?\s*([A-Z0-9\-\.]{3,20})",
                r"(?:expediente|file|exp\.)\s*:?\s*([A-Z0-9\-\.]{3,20})",
                r"(?:matrícula|matricula|matr\.)\s*:?\s*([A-Z0-9\-\.]{3,20})",
            ],
            "calificacion": [
                r"(?:calificación|grade|nota|score|puntaje|rating)\s*:?\s*([A-Z0-9\.,]+)",
                r"(?:promedio|average|gpa|media)\s*:?\s*([0-9\.,]+)",
                r"(?:con un promedio|with an average|average of)\s+([0-9\.,]+)",
                r"(?:aprobado|approved|passed|reprobado|failed|rejected)",
            ],
            "duracion": [
                r"(?:duración|duration|período|period|tiempo|time)\s*:?\s*([A-Z0-9\s]+)",
                r"(\d+)\s*(?:años|years|año|year|meses|months|mes|month|semestres|semesters|semestre|semester)",
                r"(?:carga horaria|workload|horas totales|total hours)\s*:?\s*(\d+)",
                r"(?:durante|during|for)\s+(\d+)\s*(?:años|years|año|year)",
            ],
            "modalidad": [
                r"(?:modalidad|mode|formato|format|tipo|type)\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
                r"(?:presencial|virtual|online|distancia|distance|blended|híbrido|hybrid)\s*([A-ZÁÉÍÓÚÑ\s]*)",
            ],
            "sede": [
                r"(?:sede|campus|location|ubicación)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:ciudad|city|provincia|province|estado|state)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "facultad": [
                r"(?:facultad|faculty|departamento|department)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:de la facultad|of the faculty|del departamento|of the department)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "carrera": [
                r"(?:carrera|career|programa|program|especialidad|specialty)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:en la carrera|in the career|del programa|of the program)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "resolucion": [
                r"(?:resolución|resolution|res\.|resol\.)\s*:?\s*([A-Z0-9\-\/\.]+)",
                r"(?:expediente|file|exp\.)\s*:?\s*([A-Z0-9\-\/\.]+)",
            ]
        }
        
        # Patrones específicos para certificados
        self.certificado_patterns = {
            "institucion": [
                r"(?:certifica|certify|certificate|certificado)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"([A-ZÁÉÍÓÚÑ\s\.]+)\s+(?:certifica|certify|certificate)",
                r"(?:por la presente|hereby)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "estudiante": [
                r"(?:estudiante|alumno|student|persona|person|participante|participant)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"([A-ZÁÉÍÓÚÑ\s\.]+)\s+(?:estudiante|alumno|student|participante)",
                r"(?:señor|señora|sr\.|sra\.|mr\.|mrs\.|ms\.)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "curso_materia": [
                r"(?:curso|materia|subject|course|capacitación|training|seminario|seminar)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:asignatura|discipline|field|área|area)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:en el curso|in the course|del seminario|of the seminar)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "fecha_emision": [
                r"(?:fecha|date|issued|emisión|otorgado|granted)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?:fecha|date|issued|emisión|otorgado|granted)\s*:?\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
                r"(?:el|on)\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
            ],
            "duracion_horas": [
                r"(\d+)\s*(?:horas|hours|h\.?|hs\.?)",
                r"(?:duración|duration|carga horaria|workload)\s*:?\s*(\d+)\s*(?:horas|hours|h\.?)",
                r"(?:total de|total of)\s+(\d+)\s*(?:horas|hours|h\.?)",
            ],
            "calificacion": [
                r"(?:calificación|grade|nota|score|resultado|result)\s*:?\s*([A-Z0-9\.,]+)",
                r"(?:aprobado|approved|passed|reprobado|failed|rejected|completado|completed)",
                r"(?:promedio|average|media)\s*:?\s*([0-9\.,]+)",
            ],
            "instructor": [
                r"(?:instructor|teacher|profesor|professor|docente|facilitador|facilitator)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
                r"(?:a cargo de|in charge of|dirigido por|directed by)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            ],
            "numero_registro": [
                r"(?:registro|record|número|number|nro|nº|#)\s*:?\s*([A-Z0-9\-\.]+)",
                r"(?:código|code|cod\.)\s*:?\s*([A-Z0-9\-\.]+)",
            ]
        }
    
    def extract_titulo_data(self, text: str) -> AcademicDocumentData:
        """Extraer datos de un título académico"""
        try:
            data = AcademicDocumentData(tipo_documento="titulo")
            
            # Detectar tipo específico de título
            if self._is_diploma(text):
                data.tipo_documento = "diploma"
            elif self._is_licencia(text):
                data.tipo_documento = "licencia"
            
            # Extraer datos usando patrones
            data.institucion = self._extract_field(text, self.titulo_patterns["institucion"])
            data.titulo_otorgado = self._extract_field(text, self.titulo_patterns["titulo"])
            data.nombre_estudiante = self._extract_field(text, self.titulo_patterns["estudiante"])
            data.fecha_emision = self._extract_field(text, self.titulo_patterns["fecha_emision"])
            data.numero_registro = self._extract_field(text, self.titulo_patterns["numero_registro"])
            data.calificacion = self._extract_field(text, self.titulo_patterns["calificacion"])
            data.duracion = self._extract_field(text, self.titulo_patterns["duracion"])
            data.modalidad = self._extract_field(text, self.titulo_patterns["modalidad"])
            data.sede = self._extract_field(text, self.titulo_patterns["sede"])
            data.facultad = self._extract_field(text, self.titulo_patterns["facultad"])
            data.carrera = self._extract_field(text, self.titulo_patterns["carrera"])
            data.resolucion = self._extract_field(text, self.titulo_patterns["resolucion"])
            
            # Extraer datos específicos adicionales
            data.nivel_academico = self._extract_academic_level(text)
            data.area_estudio = self._extract_study_area(text)
            data.creditos = self._extract_credits(text)
            data.horas_cursadas = self._extract_hours(text)
            data.director_tesis = self._extract_thesis_director(text)
            data.jurado = self._extract_committee(text)
            data.codigo_verificacion = self._extract_verification_code(text)
            data.numero_documento = self._extract_document_number(text)
            data.fecha_vencimiento = self._extract_expiration_date(text)
            data.validez_nacional = self._extract_national_validity(text)
            data.equivalencia = self._extract_equivalence(text)
            
            # Post-procesar datos para mejorar precisión
            data = self._post_process_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de título: {e}")
            return AcademicDocumentData(tipo_documento="titulo")
    
    def _post_process_data(self, data: AcademicDocumentData) -> AcademicDocumentData:
        """Post-procesar y limpiar los datos extraídos"""
        # Limpiar nombres de instituciones
        if data.institucion:
            data.institucion = self._clean_institution_name(data.institucion)
        
        # Limpiar nombres de estudiantes
        if data.nombre_estudiante:
            data.nombre_estudiante = self._clean_student_name(data.nombre_estudiante)
        
        # Limpiar títulos
        if data.titulo_otorgado:
            data.titulo_otorgado = self._clean_title(data.titulo_otorgado)
        
        # Validar y formatear fechas
        if data.fecha_emision:
            data.fecha_emision = self._format_date(data.fecha_emision)
        
        if data.fecha_vencimiento:
            data.fecha_vencimiento = self._format_date(data.fecha_vencimiento)
        
        # Limpiar códigos de verificación
        if data.codigo_verificacion:
            data.codigo_verificacion = self._clean_verification_code(data.codigo_verificacion)
        
        return data
    
    def _clean_institution_name(self, name: str) -> str:
        """Limpiar nombre de institución"""
        # Remover palabras comunes que no son parte del nombre
        common_words = ['facultad', 'departamento', 'de', 'del', 'la', 'el', 'university', 'institute', 'college']
        words = name.split()
        cleaned_words = [word for word in words if word.lower() not in common_words]
        
        # Tomar solo las primeras palabras relevantes
        if len(cleaned_words) > 4:
            cleaned_words = cleaned_words[:4]
        
        return ' '.join(cleaned_words).strip()
    
    def _clean_student_name(self, name: str) -> str:
        """Limpiar nombre de estudiante"""
        # Remover DNI y otros números
        name = re.sub(r'\d{7,8}', '', name)
        name = re.sub(r'DNI\s*:?\s*', '', name, flags=re.IGNORECASE)
        
        # Limpiar espacios y caracteres especiales
        name = re.sub(r'\s+', ' ', name)
        name = name.strip('.,:;')
        
        return name
    
    def _clean_title(self, title: str) -> str:
        """Limpiar título otorgado"""
        # Remover palabras comunes
        common_words = ['título', 'de', 'en', 'title', 'degree', 'diploma']
        words = title.split()
        cleaned_words = [word for word in words if word.lower() not in common_words]
        
        return ' '.join(cleaned_words).strip()
    
    def _format_date(self, date: str) -> str:
        """Formatear fecha a formato estándar"""
        # Intentar diferentes formatos de fecha
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date)
            if match:
                if '/' in date or '-' in date:
                    # Formato DD/MM/YYYY o DD-MM-YYYY
                    day, month, year = match.groups()
                    if len(year) == 2:
                        year = '20' + year
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                else:
                    # Formato DD de mes de YYYY
                    day, month_name, year = match.groups()
                    month_map = {
                        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                    }
                    month = month_map.get(month_name.lower(), '01')
                    return f"{day.zfill(2)}/{month}/{year}"
        
        return date
    
    def _clean_verification_code(self, code: str) -> str:
        """Limpiar código de verificación"""
        # Remover texto descriptivo
        code = re.sub(r'(?:código|código de verificación|verification code|verificar|verify|check)\s*:?\s*', '', code, flags=re.IGNORECASE)
        code = code.strip()
        
        # Validar formato
        if re.match(r'^[A-Z0-9\-]{3,20}$', code):
            return code
        
        return None
    
    def extract_certificado_data(self, text: str) -> AcademicDocumentData:
        """Extraer datos de un certificado"""
        try:
            data = AcademicDocumentData(tipo_documento="certificado")
            
            # Extraer datos usando patrones de certificado
            data.institucion = self._extract_field(text, self.certificado_patterns["institucion"])
            data.nombre_estudiante = self._extract_field(text, self.certificado_patterns["estudiante"])
            data.fecha_emision = self._extract_field(text, self.certificado_patterns["fecha_emision"])
            data.calificacion = self._extract_field(text, self.certificado_patterns["calificacion"])
            data.duracion = self._extract_field(text, self.certificado_patterns["duracion_horas"])
            data.numero_registro = self._extract_field(text, self.certificado_patterns["numero_registro"])
            
            # Extraer datos específicos de certificado
            data.area_estudio = self._extract_field(text, self.certificado_patterns["curso_materia"])
            data.horas_cursadas = self._extract_hours(text)
            data.sede = self._extract_field(text, self.titulo_patterns["sede"])
            data.facultad = self._extract_field(text, self.titulo_patterns["facultad"])
            data.carrera = self._extract_field(text, self.titulo_patterns["carrera"])
            
            # Post-procesar datos para mejorar precisión
            data = self._post_process_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de certificado: {e}")
            return AcademicDocumentData(tipo_documento="certificado")
    
    def _extract_field(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extraer un campo usando múltiples patrones con validación mejorada"""
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
                result = re.sub(r'\s+', ' ', result)  # Múltiples espacios a uno
                result = result.strip('.,:;')  # Quitar puntuación al final
                
                # Validar resultado
                if self._validate_extracted_field(result):
                    # Calcular score de calidad
                    score = self._calculate_field_score(result, pattern)
                    if score > best_score:
                        best_score = score
                        best_match = result
        
        return best_match if best_match and len(best_match) > 2 else None
    
    def _validate_extracted_field(self, field: str) -> bool:
        """Validar si el campo extraído es válido"""
        if not field or len(field) < 2:
            return False
        
        # Verificar que no sea solo números o caracteres especiales
        if re.match(r'^[\d\s\-\.]+$', field):
            return False
        
        # Verificar que no contenga solo palabras muy comunes
        common_words = ['el', 'la', 'de', 'del', 'en', 'con', 'por', 'para', 'se', 'que', 'es', 'son']
        if field.lower() in common_words:
            return False
        
        # Verificar longitud razonable
        if len(field) > 200:
            return False
        
        return True
    
    def _calculate_field_score(self, field: str, pattern: str) -> float:
        """Calcular score de calidad del campo extraído"""
        score = 0.0
        
        # Bonus por longitud apropiada
        if 5 <= len(field) <= 100:
            score += 1.0
        
        # Bonus por contener letras
        if re.search(r'[A-Za-z]', field):
            score += 0.5
        
        # Bonus por no contener caracteres especiales excesivos
        special_chars = len(re.findall(r'[^\w\s]', field))
        if special_chars < len(field) * 0.3:
            score += 0.5
        
        # Bonus por patrones específicos
        if 'institucion' in pattern and re.search(r'(universidad|instituto|colegio|escuela)', field, re.IGNORECASE):
            score += 1.0
        elif 'estudiante' in pattern and re.search(r'^[A-ZÁÉÍÓÚÑ\s\.]+$', field):
            score += 1.0
        elif 'fecha' in pattern and re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', field):
            score += 1.0
        
        return score
    
    def _is_diploma(self, text: str) -> bool:
        """Detectar si es un diploma"""
        diploma_indicators = [
            "diploma", "graduación", "graduation", "egresado", "graduate",
            "completado", "completed", "finalizado", "finished"
        ]
        return any(indicator in text.lower() for indicator in diploma_indicators)
    
    def _is_licencia(self, text: str) -> bool:
        """Detectar si es una licencia"""
        licencia_indicators = [
            "licencia", "license", "habilitación", "autorización", "permiso",
            "permit", "authorization", "habilitado", "enabled"
        ]
        return any(indicator in text.lower() for indicator in licencia_indicators)
    
    def _extract_academic_level(self, text: str) -> Optional[str]:
        """Extraer nivel académico"""
        levels = {
            "pregrado": ["pregrado", "undergraduate", "bachiller", "técnico", "tecnólogo", "técnico superior"],
            "posgrado": ["posgrado", "graduate", "especialización", "maestría", "doctorado", "postgrado"],
            "doctorado": ["doctorado", "phd", "doctor", "doctoral", "doctor en", "doctor of"],
            "maestría": ["maestría", "master", "magister", "especialización", "master en", "master of"],
            "especialización": ["especialización", "specialization", "especialista", "especialista en"],
            "técnico": ["técnico", "técnico superior", "técnico universitario", "technical", "technician"],
            "bachiller": ["bachiller", "bachillerato", "bachelor", "bachelor's", "licenciado", "licenciatura"]
        }
        
        text_lower = text.lower()
        for level, keywords in levels.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        return None
    
    def _extract_study_area(self, text: str) -> Optional[str]:
        """Extraer área de estudio"""
        areas = {
            "ingeniería": ["ingeniería", "engineering", "ingeniero", "engineer"],
            "medicina": ["medicina", "medicine", "médico", "medical", "doctor"],
            "derecho": ["derecho", "law", "abogado", "lawyer", "jurídico", "legal"],
            "administración": ["administración", "administration", "administrador", "administrator", "gestión", "management"],
            "contaduría": ["contaduría", "accounting", "contador", "accountant", "contable"],
            "psicología": ["psicología", "psychology", "psicólogo", "psychologist"],
            "educación": ["educación", "education", "pedagogía", "pedagogy", "docente", "teacher"],
            "arquitectura": ["arquitectura", "architecture", "arquitecto", "architect"],
            "ciencias": ["ciencias", "sciences", "científico", "scientific", "ciencia"],
            "artes": ["artes", "arts", "artístico", "artistic", "arte", "art"],
            "informática": ["informática", "computing", "sistemas", "systems", "programación", "programming"],
            "economía": ["economía", "economics", "económico", "economic", "finanzas", "finance"],
            "comunicación": ["comunicación", "communication", "comunicador", "communicator"],
            "marketing": ["marketing", "mercadotecnia", "publicidad", "advertising"]
        }
        
        text_lower = text.lower()
        for area, keywords in areas.items():
            if any(keyword in text_lower for keyword in keywords):
                return area.title()
        return None
    
    def _extract_credits(self, text: str) -> Optional[str]:
        """Extraer créditos académicos"""
        patterns = [
            r"(\d+)\s*(?:créditos|credits|cr\.?)",
            r"(?:total de|total of)\s+(\d+)\s*(?:créditos|credits)",
            r"(?:carga académica|academic load)\s*:?\s*(\d+)\s*(?:créditos|credits)"
        ]
        return self._extract_field(text, patterns)
    
    def _extract_hours(self, text: str) -> Optional[str]:
        """Extraer horas cursadas"""
        patterns = [
            r"(\d+)\s*(?:horas|hours|h\.?|hs\.?)",
            r"(?:total de|total of)\s+(\d+)\s*(?:horas|hours)",
            r"(?:carga horaria|workload)\s*:?\s*(\d+)\s*(?:horas|hours)"
        ]
        return self._extract_field(text, patterns)
    
    def _extract_thesis_director(self, text: str) -> Optional[str]:
        """Extraer director de tesis"""
        patterns = [
            r"(?:director|director de tesis|thesis director|tutor|advisor|supervisor)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
            r"(?:dirigido por|directed by|supervisado por|supervised by)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            r"(?:bajo la dirección de|under the direction of)\s+([A-ZÁÉÍÓÚÑ\s\.]+)"
        ]
        return self._extract_field(text, patterns)
    
    def _extract_committee(self, text: str) -> List[str]:
        """Extraer miembros del jurado"""
        patterns = [
            r"(?:jurado|committee|evaluadores|evaluators|tribunal|tribunal)\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
            r"(?:evaluador|evaluator|member|miembro)\s*:?\s*([A-ZÁÉÍÓÚÑ\s,\.]+)",
            r"(?:integrado por|composed of|formado por|formed by)\s+([A-ZÁÉÍÓÚÑ\s,\.]+)"
        ]
        
        committee_text = self._extract_field(text, patterns)
        if committee_text:
            # Separar por comas y limpiar
            members = [member.strip() for member in committee_text.split(",")]
            return [member for member in members if member and len(member) > 2]
        return []
    
    def _extract_verification_code(self, text: str) -> Optional[str]:
        """Extraer código de verificación"""
        patterns = [
            r"(?:código|código de verificación|verification code|verificar|verify|check)\s*:?\s*([A-Z0-9\-]+)",
            r"(?:para verificar|to verify|verificación|verification)\s*:?\s*([A-Z0-9\-]+)",
            r"(?:código|code)\s+([A-Z0-9\-]{6,})"
        ]
        return self._extract_field(text, patterns)
    
    def _extract_document_number(self, text: str) -> Optional[str]:
        """Extraer número de documento del estudiante"""
        patterns = [
            r"(?:dni|documento|document|id|cedula|cédula)\s*:?\s*(\d{7,8})",
            r"(?:número de documento|document number)\s*:?\s*(\d{7,8})",
            r"(\d{7,8})\s*(?:dni|documento|document)"
        ]
        return self._extract_field(text, patterns)
    
    def _extract_expiration_date(self, text: str) -> Optional[str]:
        """Extraer fecha de vencimiento"""
        patterns = [
            r"(?:vencimiento|expiration|expires|válido hasta|valid until)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(?:vencimiento|expiration|expires|válido hasta|valid until)\s*:?\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        ]
        return self._extract_field(text, patterns)
    
    def _extract_national_validity(self, text: str) -> Optional[str]:
        """Extraer validez nacional"""
        patterns = [
            r"(?:validez nacional|national validity|válido en|valid in)\s*:?\s*([A-ZÁÉÍÓÚÑ\s]+)",
            r"(?:reconocido en|recognized in)\s+([A-ZÁÉÍÓÚÑ\s]+)",
        ]
        return self._extract_field(text, patterns)
    
    def _extract_equivalence(self, text: str) -> Optional[str]:
        """Extraer equivalencia"""
        patterns = [
            r"(?:equivalente a|equivalent to|equivale a|equals to)\s+([A-ZÁÉÍÓÚÑ\s\.]+)",
            r"(?:equivalencia|equivalence)\s*:?\s*([A-ZÁÉÍÓÚÑ\s\.]+)",
        ]
        return self._extract_field(text, patterns)

# Instancia global del servicio
_academic_extraction_service = None

def get_academic_extraction_service() -> AcademicDocumentExtractionService:
    """Obtener instancia del servicio de extracción académica"""
    global _academic_extraction_service
    if _academic_extraction_service is None:
        _academic_extraction_service = AcademicDocumentExtractionService()
    return _academic_extraction_service
