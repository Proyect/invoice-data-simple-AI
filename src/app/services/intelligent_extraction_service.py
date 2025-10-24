import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import openai
import re
import spacy
import json
from ..core.config import settings

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    FACTURA = "factura"
    RECIBO = "recibo"
    CONTRATO = "contrato"
    FORMULARIO = "formulario"
    TITULO = "titulo"
    CERTIFICADO = "certificado"
    DIPLOMA = "diploma"
    LICENCIA = "licencia"
    DNI = "dni"
    DNI_TARJETA = "dni_tarjeta"
    DNI_LIBRETA = "dni_libreta"
    PASAPORTE = "pasaporte"
    DESCONOCIDO = "desconocido"

@dataclass
class ExtractedData:
    document_type: DocumentType
    confidence: float
    entities: Dict[str, Any]
    structured_data: Dict[str, Any]
    metadata: Dict[str, Any]

class IntelligentExtractionService:
    """
    Servicio de extracción inteligente usando LLMs y NLP
    """
    
    def __init__(self):
        # Configurar OpenAI
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client inicializado")
        else:
            logger.warning("OpenAI API key no configurada")
        
        # LangChain no es obligatorio para los tests; evitar importaciones pesadas
        # Mantener lógica basada en OpenAI SDK oficial
        
        # Cargar spaCy (fallback)
        try:
            self.nlp = spacy.load("es_core_news_sm")
            logger.info("spaCy model cargado correctamente")
        except:
            self.nlp = None
            logger.warning("spaCy no disponible, usando solo LLMs")
        
        # Patrones de documentos
        self.document_patterns = {
            DocumentType.FACTURA: [
                r"FACTURA\s*N[º°]?",
                r"INVOICE\s*N[º°]?",
                r"FACT\s*N[º°]?",
                r"EMISOR.*RECEPTOR"
            ],
            DocumentType.RECIBO: [
                r"RECIBO",
                r"COMPROBANTE",
                r"RECEIPT"
            ],
            DocumentType.CONTRATO: [
                r"CONTRATO",
                r"ACUERDO",
                r"CONVENIO"
            ],
            DocumentType.FORMULARIO: [
                r"FORMULARIO",
                r"SOLICITUD",
                r"FORM"
            ],
            DocumentType.TITULO: [
                r"TÍTULO",
                r"TITLE",
                r"DEGREE",
                r"DIPLOMA",
                r"BACHILLER",
                r"LICENCIADO",
                r"INGENIERO",
                r"DOCTOR",
                r"MAGISTER",
                r"MASTER"
            ],
            DocumentType.CERTIFICADO: [
                r"CERTIFICADO",
                r"CERTIFICATE",
                r"CERTIFICA",
                r"CERTIFY",
                r"CURSO",
                r"COURSE",
                r"CAPACITACIÓN",
                r"TRAINING"
            ],
            DocumentType.DIPLOMA: [
                r"DIPLOMA",
                r"GRADUACIÓN",
                r"GRADUATION",
                r"EGRESADO",
                r"GRADUATE"
            ],
            DocumentType.LICENCIA: [
                r"LICENCIA",
                r"LICENSE",
                r"HABILITACIÓN",
                r"AUTORIZACIÓN",
                r"PERMISO"
            ],
            DocumentType.DNI: [
                r"DOCUMENTO\s+NACIONAL\s+DE\s+IDENTIDAD",
                r"DNI",
                r"DOCUMENTO\s+DE\s+IDENTIDAD",
                r"IDENTIDAD"
            ],
            DocumentType.DNI_TARJETA: [
                r"REPÚBLICA\s+ARGENTINA",
                r"DNI\s+TARJETA",
                r"TARJETA\s+DE\s+IDENTIDAD"
            ],
            DocumentType.DNI_LIBRETA: [
                r"LIBRETA\s+CÍVICA",
                r"LIBRETA\s+CIVICA",
                r"LC\s*:?\s*\d{7,8}"
            ],
            DocumentType.PASAPORTE: [
                r"PASAPORTE",
                r"PASSPORT",
                r"REPÚBLICA\s+ARGENTINA\s+PASAPORTE"
            ]
        }
    
    async def extract_intelligent_data(self, text: str, image_path: str = None) -> ExtractedData:
        """
        Extrae datos usando inteligencia artificial
        """
        
        try:
            # Paso 1: Detectar tipo de documento
            doc_type = self._detect_document_type(text)
            
            # Paso 2: Extraer datos con LLM
            llm_data = await self._extract_with_llm(text, doc_type)
            
            # Paso 3: Validar con spaCy (si está disponible)
            spacy_data = await self._extract_with_spacy(text)
            
            # Paso 4: Combinar y validar resultados
            combined_data = self._combine_extraction_results(llm_data, spacy_data)
            
            # Paso 5: Validar coherencia
            validated_data = self._validate_data_coherence(combined_data, doc_type)
            
            return ExtractedData(
                document_type=doc_type,
                confidence=validated_data.get('confidence', 0.8),
                entities=validated_data.get('entities', {}),
                structured_data=validated_data.get('structured_data', {}),
                metadata={
                    'extraction_method': 'llm_spacy_hybrid',
                    'llm_used': llm_data.get('confidence', 0) > 0,
                    'spacy_used': self.nlp is not None,
                    'validation_passed': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error en extracción inteligente: {e}")
            return await self._fallback_extraction(text)
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """Detecta el tipo de documento"""
        text_upper = text.upper()
        
        # Heurística directa robusta: si contiene palabras clave claras
        if "FACTURA" in text_upper:
            return DocumentType.FACTURA
        if "RECIBO" in text_upper:
            return DocumentType.RECIBO
        
        # Fallback a patrones configurados
        for doc_type, patterns in self.document_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    return doc_type
        
        return DocumentType.DESCONOCIDO
    
    async def _extract_with_llm(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Extrae datos usando LLM (OpenAI)"""
        
        if not self.openai_client:
            logger.warning("OpenAI no disponible")
            return {'method': 'openai_gpt', 'data': {}, 'confidence': 0.0}
        
        try:
            # Prompt específico por tipo de documento
            prompt = self._create_extraction_prompt(text, doc_type)
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de datos de documentos. Responde solo en formato JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parsear respuesta JSON
            llm_data = json.loads(response.choices[0].message.content)
            
            return {
                'method': 'openai_gpt',
                'data': llm_data,
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error con LLM: {e}")
            return {'method': 'openai_gpt', 'data': {}, 'confidence': 0.0}
    
    def _create_extraction_prompt(self, text: str, doc_type: DocumentType) -> str:
        """Crea prompt específico para el tipo de documento"""
        
        # Limitar tamaño del texto para evitar límites de tokens
        limited_text = text[:2000] if len(text) > 2000 else text
        
        base_prompt = f"""
        Extrae los siguientes datos del texto de un documento de tipo {doc_type.value}:
        
        Texto del documento:
        {limited_text}
        
        Devuelve un JSON con exactamente estos campos:
        """
        
        if doc_type == DocumentType.FACTURA:
            prompt = base_prompt + """
            {
                "numero_factura": "número de factura",
                "fecha": "fecha de emisión",
                "emisor": {
                    "nombre": "nombre del emisor",
                    "cuit": "CUIT del emisor",
                    "direccion": "dirección del emisor"
                },
                "receptor": {
                    "nombre": "nombre del receptor",
                    "cuit": "CUIT del receptor"
                },
                "items": [
                    {
                        "descripcion": "descripción del producto/servicio",
                        "cantidad": "cantidad",
                        "precio_unitario": "precio unitario",
                        "subtotal": "subtotal"
                    }
                ],
                "totales": {
                    "subtotal": "subtotal",
                    "iva": "IVA",
                    "total": "total final"
                },
                "forma_pago": "forma de pago",
                "vencimiento": "fecha de vencimiento"
            }
            """
        
        elif doc_type == DocumentType.RECIBO:
            prompt = base_prompt + """
            {
                "numero_recibo": "número de recibo",
                "fecha": "fecha",
                "emisor": "quien emite el recibo",
                "receptor": "quien recibe el pago",
                "concepto": "concepto del pago",
                "monto": "monto pagado",
                "forma_pago": "forma de pago"
            }
            """
        
        else:
            prompt = base_prompt + """
            {
                "fecha": "fecha del documento",
                "partes": ["partes involucradas"],
                "concepto": "concepto principal",
                "montos": ["montos mencionados"],
                "fechas": ["todas las fechas encontradas"],
                "personas": ["nombres de personas"],
                "organizaciones": ["nombres de organizaciones"]
            }
            """
        
        return prompt
    
    async def _extract_with_spacy(self, text: str) -> Dict[str, Any]:
        """Extrae datos usando spaCy (fallback)"""
        
        if not self.nlp:
            return {'method': 'spacy', 'data': {}, 'confidence': 0.0}
        
        try:
            doc = self.nlp(text)
            
            entities = {
                'personas': [],
                'organizaciones': [],
                'lugares': [],
                'fechas': [],
                'dinero': []
            }
            
            for ent in doc.ents:
                if ent.label_ == 'PER':
                    entities['personas'].append(ent.text)
                elif ent.label_ == 'ORG':
                    entities['organizaciones'].append(ent.text)
                elif ent.label_ == 'LOC':
                    entities['lugares'].append(ent.text)
                elif ent.label_ == 'DATE':
                    entities['fechas'].append(ent.text)
                elif ent.label_ == 'MONEY':
                    entities['dinero'].append(ent.text)
            
            # Eliminar duplicados
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return {
                'method': 'spacy',
                'data': entities,
                'confidence': 0.7
            }
            
        except Exception as e:
            logger.error(f"Error con spaCy: {e}")
            return {'method': 'spacy', 'data': {}, 'confidence': 0.0}
    
    def _combine_extraction_results(self, llm_data: Dict, spacy_data: Dict) -> Dict[str, Any]:
        """Combina resultados de LLM y spaCy"""
        
        combined = {
            'confidence': 0.0,
            'entities': {},
            'structured_data': {}
        }
        
        # Usar datos del LLM como base
        if llm_data.get('confidence', 0) > 0:
            combined['structured_data'] = llm_data.get('data', {})
            combined['confidence'] = llm_data.get('confidence', 0)
        
        # Complementar con entidades de spaCy
        if spacy_data.get('confidence', 0) > 0:
            combined['entities'] = spacy_data.get('data', {})
            # Promediar confianza
            combined['confidence'] = (combined['confidence'] + spacy_data.get('confidence', 0)) / 2
        
        return combined
    
    def _validate_data_coherence(self, data: Dict[str, Any], doc_type: DocumentType) -> Dict[str, Any]:
        """Valida coherencia de los datos extraídos"""
        
        validation_errors = []
        
        # Validaciones específicas por tipo
        if doc_type == DocumentType.FACTURA:
            structured = data.get('structured_data', {})
            
            # Validar que tenga número de factura
            if not structured.get('numero_factura'):
                validation_errors.append("Falta número de factura")
            
            # Validar que tenga fecha
            if not structured.get('fecha'):
                validation_errors.append("Falta fecha")
            
            # Validar que tenga total
            if not structured.get('totales', {}).get('total'):
                validation_errors.append("Falta total")
        
        elif doc_type == DocumentType.RECIBO:
            structured = data.get('structured_data', {})
            
            if not structured.get('monto'):
                validation_errors.append("Falta monto en recibo")
        
        # Ajustar confianza basada en errores
        if validation_errors:
            data['confidence'] = max(0.0, data['confidence'] - len(validation_errors) * 0.1)
            data['validation_errors'] = validation_errors
        
        return data
    
    async def _fallback_extraction(self, text: str) -> ExtractedData:
        """Fallback usando solo regex"""
        
        # Extracción básica con regex
        basic_data = self._extract_with_regex(text)
        
        return ExtractedData(
            document_type=DocumentType.DESCONOCIDO,
            confidence=0.5,
            entities={},
            structured_data=basic_data,
            metadata={
                'extraction_method': 'regex_fallback',
                'llm_used': False,
                'spacy_used': False,
                'validation_passed': False
            }
        )
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """Extracción básica con regex"""
        
        patterns = {
            'fecha': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'monto': r'(\$\s?\d+[\d\.,]*)',
            'cuit': r'(\d{2}-?\d{8}-?\d{1})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'telefono': r'(\+?54\s?9?\d{2,4}\s?\d{6,8})'
        }
        
        extracted = {}
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted[key] = matches[0] if len(matches) == 1 else matches
        
        return extracted
