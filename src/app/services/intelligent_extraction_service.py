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
            
            # Para facturas, usar más tokens y temperatura más baja para mayor precisión
            if doc_type == DocumentType.FACTURA:
                max_tokens = min(2000, settings.OPENAI_MAX_TOKENS * 2)  # Más tokens para facturas
                temperature = 0.0  # Temperatura 0 para máxima precisión en facturas
            else:
                max_tokens = settings.OPENAI_MAX_TOKENS
                temperature = settings.OPENAI_TEMPERATURE
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de datos de documentos argentinos, especialmente facturas. Responde SOLO en formato JSON válido, sin texto adicional. Si un campo no existe, usa null."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if doc_type == DocumentType.FACTURA else None  # Forzar JSON para facturas
            )
            
            # Parsear respuesta JSON
            content = response.choices[0].message.content.strip()
            
            # Limpiar contenido si tiene markdown code blocks
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            try:
                llm_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del LLM: {e}")
                logger.error(f"Contenido recibido: {content[:500]}")
                # Intentar extraer JSON del texto si está embebido
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        llm_data = json.loads(json_match.group())
                    except:
                        llm_data = {}
                else:
                    llm_data = {}
            
            # Calcular confianza basada en completitud de datos para facturas
            confidence = 0.9
            if doc_type == DocumentType.FACTURA:
                # Verificar que tenga campos críticos
                critical_fields = ['numero_factura', 'fecha_emision', 'emisor', 'totales']
                found_critical = sum(1 for field in critical_fields if llm_data.get(field))
                
                # Verificar campos importantes adicionales
                important_fields = ['items', 'receptor', 'cae']
                found_important = sum(1 for field in important_fields if llm_data.get(field))
                
                # Verificar completitud de items
                items = llm_data.get('items', [])
                items_completos = 0
                if items and len(items) > 0:
                    for item in items:
                        if item.get('descripcion') and item.get('subtotal'):
                            items_completos += 1
                    items_score = items_completos / len(items) if items else 0
                else:
                    items_score = 0
                
                # Verificar completitud de totales
                totales = llm_data.get('totales', {})
                totales_completos = 0
                if totales.get('subtotal') or totales.get('subtotal_sin_iva'):
                    totales_completos += 1
                if totales.get('total') or totales.get('importe_total'):
                    totales_completos += 1
                if totales.get('importe_otros_tributos') is not None:
                    totales_completos += 1
                totales_score = totales_completos / 3 if totales_completos > 0 else 0
                
                # Calcular confianza combinada
                critical_score = found_critical / len(critical_fields)
                important_score = found_important / len(important_fields) if found_important > 0 else 0.5
                
                # Confianza final: promedio ponderado
                confidence = (critical_score * 0.5) + (important_score * 0.2) + (items_score * 0.2) + (totales_score * 0.1)
                confidence = min(0.98, max(0.5, confidence))  # Limitar entre 0.5 y 0.98
            
            return {
                'method': 'openai_gpt',
                'data': llm_data,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error con LLM: {e}")
            return {'method': 'openai_gpt', 'data': {}, 'confidence': 0.0}
    
    def _create_extraction_prompt(self, text: str, doc_type: DocumentType) -> str:
        """Crea prompt específico para el tipo de documento"""
        
        # Limitar tamaño del texto para evitar límites de tokens, pero mantener más texto para facturas
        if doc_type == DocumentType.FACTURA:
            # Para facturas argentinas, mantener TODO el texto para capturar todos los items y totales
            # Las facturas argentinas pueden tener muchos items, así que necesitamos más texto
            limited_text = text[:8000] if len(text) > 8000 else text
        else:
            limited_text = text[:2000] if len(text) > 2000 else text
        
        base_prompt = f"""
        Extrae los siguientes datos del texto de un documento de tipo {doc_type.value}:
        
        Texto del documento:
        {limited_text}
        
        Devuelve un JSON con exactamente estos campos:
        """
        
        if doc_type == DocumentType.FACTURA:
            prompt = base_prompt + """
            Eres un experto en facturas electrónicas argentinas (AFIP). Debes extraer TODOS los datos con máxima precisión.
            
            INSTRUCCIONES CRÍTICAS:
            1. Lee TODO el texto, línea por línea, sin omitir nada
            2. Busca en TODAS las secciones: encabezado, emisor, receptor, items/tabla, totales, pie de página
            3. Para items: busca tablas con columnas como "Código", "Producto/Servicio", "Cantidad", "U. Medida", "Precio Unit.", "% Bonif", "Imp. Bonif", "Subtotal"
            4. Para totales: busca "Subtotal", "Importe Otros Tributos", "Importe Total" (pueden estar en una caja o sección separada)
            5. Si hay descripción adicional fuera de la tabla (ej: texto en cursiva o entre comillas), inclúyela en "descripcion_adicional"
            6. Para CAE: busca "CAE N°:" o "CAE:" seguido de 14 dígitos
            7. Para fechas: busca "Fecha de Emisión", "Fecha de Vto.", "Período Facturado Desde/Hasta"
            8. NO resumas descripciones, copia TODO el texto exactamente como aparece
            
            Devuelve un JSON válido con exactamente estos campos (usa null si no encuentras el dato):
            {
                "numero_factura": "número completo de factura (ej: 0001-00001234 o 00002-00000014)",
                "punto_venta": "punto de venta (número antes del guión, ej: 00002)",
                "numero_comprobante": "número de comprobante (número después del guión, ej: 00000014)",
                "tipo_comprobante": "tipo de comprobante (A, B, C, E, etc.)",
                "codigo_comprobante": "código del comprobante si aparece (ej: COD. 011)",
                "fecha_emision": "fecha de emisión (formato DD/MM/YYYY)",
                "fecha_vencimiento": "fecha de vencimiento para el pago si existe",
                "periodo_facturado_desde": "fecha desde del período facturado si existe",
                "periodo_facturado_hasta": "fecha hasta del período facturado si existe",
                "cae": "Código de Autorización Electrónico (CAE) completo de 14 dígitos si existe",
                "cae_vencimiento": "fecha de vencimiento del CAE (formato DD/MM/YYYY)",
                "emisor": {
                    "razon_social": "razón social completa del emisor",
                    "nombre_fantasia": "nombre de fantasía si existe",
                    "cuit": "CUIT del emisor (formato XX-XXXXXXXX-X)",
                    "ingresos_brutos": "número de ingresos brutos si existe",
                    "condicion_iva": "condición frente al IVA (Responsable Inscripto, Exento, etc.)",
                    "domicilio_fiscal": "domicilio fiscal completo",
                    "localidad": "localidad",
                    "provincia": "provincia",
                    "codigo_postal": "código postal",
                    "telefono": "teléfono",
                    "email": "email",
                    "inicio_actividades": "fecha de inicio de actividades si aparece"
                },
                "receptor": {
                    "razon_social": "razón social completa del receptor",
                    "nombre_fantasia": "nombre de fantasía si existe",
                    "cuit": "CUIT del receptor (formato XX-XXXXXXXX-X)",
                    "condicion_iva": "condición frente al IVA del receptor",
                    "domicilio": "domicilio del receptor",
                    "localidad": "localidad del receptor",
                    "provincia": "provincia del receptor",
                    "codigo_postal": "código postal del receptor"
                },
                "items": [
                    {
                        "codigo": "código del producto/servicio si existe",
                        "descripcion": "descripción COMPLETA y DETALLADA del producto o servicio (MUY IMPORTANTE: extrae toda la descripción, no la resumas)",
                        "descripcion_adicional": "descripción adicional o detalle complementario si aparece en otra sección de la factura (ej: 'Desarrollo de sistemas - Sitios web...')",
                        "cantidad": "cantidad (número con decimales si aplica, ej: 1,00)",
                        "unidad_medida": "unidad de medida (unidad, unidades, kg, m, etc.)",
                        "precio_unitario": "precio unitario sin IVA (formato argentino: 60000,00)",
                        "porcentaje_bonificacion": "porcentaje de bonificación si existe (ej: 0,00)",
                        "importe_bonificacion": "importe de bonificación si existe (ej: 0,00)",
                        "alicuota_iva": "alícuota de IVA (21, 10.5, 0, etc.)",
                        "subtotal": "subtotal del item sin IVA (formato argentino: 60000,00)",
                        "iva_item": "IVA del item si se calcula por item",
                        "total_item": "total del item con IVA si aplica"
                    }
                ],
                "totales": {
                    "subtotal": "subtotal sin IVA (importe neto gravado + importe neto no gravado, formato: 60000,00)",
                    "subtotal_sin_iva": "subtotal sin IVA",
                    "importe_neto_gravado": "importe neto gravado",
                    "importe_neto_no_gravado": "importe neto no gravado",
                    "iva_21": "IVA al 21%",
                    "iva_10_5": "IVA al 10.5%",
                    "iva_27": "IVA al 27%",
                    "iva_0": "operaciones exentas",
                    "total_iva": "total de IVA",
                    "impuestos_internos": "impuestos internos si existen",
                    "percepciones_iva": "percepciones de IVA si existen",
                    "percepciones_ingresos_brutos": "percepciones de ingresos brutos si existen",
                    "percepciones_otras": "otras percepciones si existen",
                    "total_percepciones": "total de percepciones",
                    "retenciones": "retenciones si existen",
                    "total_retenciones": "total de retenciones",
                    "otros_tributos": "otros tributos si existen",
                    "importe_otros_tributos": "importe de otros tributos (puede aparecer como 'Importe Otros Tributos')",
                    "total_otros_tributos": "total de otros tributos",
                    "importe_total": "importe total (puede aparecer como 'Importe Total')",
                    "total": "total final a pagar (formato: 60000,00)",
                    "moneda": "moneda (ARS, USD, etc.)"
                },
                "forma_pago": "forma de pago (Efectivo, Transferencia, Cheque, etc.)",
                "condicion_venta": "condición de venta (Contado, Cuenta Corriente, etc.)",
                "observaciones": "observaciones o notas adicionales",
                "referencias": "referencias a otros comprobantes si existen",
                "codigo_qr": "código QR o datos del código QR si es visible",
                "codigo_barras": "código de barras si existe"
            }
            
            EJEMPLOS DE FORMATOS ESPERADOS:
            
            Número de factura: "00002-00000014" o "0001-00001234"
            Punto de venta: "00002" o "0001"
            CAE: "75403938202167" (14 dígitos exactos)
            Fecha: "07/10/2025" o "17/10/2025"
            CUIT: "20296451143" o "20-29645114-3" o "30717009718"
            Montos: "60000,00" o "$60000,00" o "60.000,00"
            Descripción item: "mantenimiento y limpieza de sistemas" (COMPLETA, sin resumir)
            Descripción adicional: "Desarrollo de sistemas - Sitios web - APP - redes y servidores https://www.infrasoft.com.ar/"
            
            VALIDACIONES CRÍTICAS:
            - Si encuentras una tabla de items, extrae TODAS las filas
            - Si hay texto descriptivo fuera de la tabla, es "descripcion_adicional"
            - "Subtotal" puede aparecer como "$60000,00" o "60000,00"
            - "Importe Otros Tributos" puede ser "$0,00" o "0,00"
            - "Importe Total" es el total final, puede ser igual a subtotal en facturas tipo C
            - Para facturas tipo C (Monotributo): no hay IVA desglosado, subtotal = total generalmente
            - Período facturado: busca "Período Facturado Desde" y "Hasta" o "Desde" y "Hasta"
            - Condición de venta: busca "Condición de venta" o "Cond. de venta" (ej: "Contado")
            
            ESTRUCTURA DE BÚSQUEDA:
            1. ENCABEZADO: número factura, punto venta, tipo, fechas, CAE
            2. EMISOR: razón social, CUIT, domicilio, condición IVA, ingresos brutos, inicio actividades
            3. RECEPTOR: razón social, CUIT, domicilio, condición IVA
            4. TABLA DE ITEMS: código, descripción, cantidad, unidad, precio, bonificación, subtotal
            5. DESCRIPCIÓN ADICIONAL: texto fuera de la tabla (puede estar en cursiva, entre comillas, o en sección separada)
            6. TOTALES: subtotal, otros tributos, importe total (pueden estar en caja o sección destacada)
            7. PIE: CAE, fecha vencimiento CAE, observaciones
            
            IMPORTANTE: Si un campo no aparece, usa null. NO inventes datos. Si hay ambigüedad, elige el valor más probable.
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
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia y depura los datos extraídos"""
        if not isinstance(data, dict):
            return data
        
        cleaned = {}
        
        for key, value in data.items():
            if value is None:
                continue
            
            # Limpiar strings
            if isinstance(value, str):
                # Remover espacios extra al inicio y final
                value = value.strip()
                # Si está vacío después de limpiar, omitir
                if not value or value.lower() == 'null' or value.lower() == 'none':
                    continue
                cleaned[key] = value
            
            # Limpiar diccionarios anidados
            elif isinstance(value, dict):
                cleaned_dict = self._clean_extracted_data(value)
                if cleaned_dict:  # Solo incluir si tiene contenido
                    cleaned[key] = cleaned_dict
            
            # Limpiar listas
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_item = self._clean_extracted_data(item)
                        if cleaned_item:  # Solo incluir items con contenido
                            cleaned_list.append(cleaned_item)
                    elif item and str(item).strip() and str(item).lower() not in ['null', 'none', '']:
                        cleaned_list.append(item)
                if cleaned_list:
                    cleaned[key] = cleaned_list
            
            # Otros tipos (números, booleanos, etc.)
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _validate_data_coherence(self, data: Dict[str, Any], doc_type: DocumentType) -> Dict[str, Any]:
        """Valida coherencia de los datos extraídos"""
        
        validation_errors = []
        
        # Validaciones específicas por tipo
        if doc_type == DocumentType.FACTURA:
            structured = data.get('structured_data', {})
            
            # Validaciones críticas (reducen confianza significativamente)
            critical_fields = []
            if not structured.get('numero_factura'):
                critical_fields.append("numero_factura")
            if not structured.get('fecha_emision'):
                critical_fields.append("fecha_emision")
            # Para facturas tipo C (Monotributo), puede no haber total en totales, pero sí importe_total
            totales_dict = structured.get('totales', {})
            if not totales_dict.get('total') and not totales_dict.get('importe_total'):
                critical_fields.append("total")
            if not structured.get('emisor', {}).get('razon_social') and not structured.get('emisor', {}).get('cuit'):
                critical_fields.append("emisor")
            
            if critical_fields:
                validation_errors.append(f"Campos críticos faltantes: {', '.join(critical_fields)}")
            
            # Validaciones importantes (reducen confianza moderadamente)
            important_fields = []
            if not structured.get('emisor', {}).get('cuit'):
                important_fields.append("CUIT emisor")
            if not structured.get('totales', {}).get('total_iva') and not structured.get('totales', {}).get('iva_21'):
                important_fields.append("IVA")
            # Validar que haya items o al menos descripción de servicios
            items = structured.get('items', [])
            if not items or len(items) == 0:
                # Verificar si hay descripción en otra parte
                if not structured.get('descripcion_adicional') and not structured.get('observaciones'):
                    important_fields.append("items")
            else:
                # Validar que los items tengan descripción
                items_sin_descripcion = [item for item in items if not item.get('descripcion')]
                if len(items_sin_descripcion) > 0:
                    important_fields.append("items sin descripción completa")
            
            if important_fields:
                validation_errors.append(f"Campos importantes faltantes: {', '.join(important_fields)}")
            
            # Validaciones de coherencia
            emisor = structured.get('emisor', {})
            receptor = structured.get('receptor', {})
            totales = structured.get('totales', {})
            
            # Validar formato de CUIT si existe
            if emisor.get('cuit'):
                cuit = emisor['cuit'].replace('-', '').replace(' ', '')
                if len(cuit) != 11 or not cuit.isdigit():
                    validation_errors.append("CUIT emisor con formato inválido")
            
            if receptor.get('cuit'):
                cuit = receptor['cuit'].replace('-', '').replace(' ', '')
                if len(cuit) != 11 or not cuit.isdigit():
                    validation_errors.append("CUIT receptor con formato inválido")
            
            # Validar que los totales sean coherentes
            # Para facturas tipo C (Monotributo), puede no haber IVA, solo subtotal = total
            total_final = totales.get('total') or totales.get('importe_total')
            subtotal_val = totales.get('subtotal') or totales.get('subtotal_sin_iva')
            total_iva = totales.get('total_iva', 0)
            importe_otros_tributos = totales.get('importe_otros_tributos') or totales.get('total_otros_tributos') or 0
            
            if total_final and subtotal_val:
                try:
                    # Convertir formato argentino (60000,00) a float
                    def parse_amount(amount_str):
                        if not amount_str:
                            return 0.0
                        # Remover símbolos y espacios
                        amount_str = str(amount_str).replace('$', '').replace(' ', '').strip()
                        # Reemplazar punto de miles y coma decimal
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                        return float(amount_str)
                    
                    subtotal = parse_amount(subtotal_val)
                    iva = parse_amount(total_iva) if total_iva else 0.0
                    otros_trib = parse_amount(importe_otros_tributos) if importe_otros_tributos else 0.0
                    total_calc = parse_amount(total_final)
                    
                    # Para facturas tipo C, total puede ser igual a subtotal (sin IVA)
                    # Para facturas tipo A/B, total = subtotal + IVA + otros tributos
                    total_expected = subtotal + iva + otros_trib
                    
                    # Permitir diferencia de hasta 1 peso por redondeo
                    if abs(total_calc - total_expected) > 1.0 and abs(total_calc - subtotal) > 1.0:
                        validation_errors.append("Incoherencia en totales (subtotal + IVA + otros tributos ≠ total)")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error validando totales: {e}")
                    pass
            
            # Validar que haya items si hay totales
            items = structured.get('items', [])
            if items and (totales.get('subtotal') or totales.get('subtotal_sin_iva')):
                try:
                    def parse_amount(amount_str):
                        if not amount_str:
                            return 0.0
                        amount_str = str(amount_str).replace('$', '').replace(' ', '').strip()
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                        return float(amount_str)
                    
                    items_total = sum(parse_amount(item.get('total_item', item.get('subtotal', 0))) for item in items)
                    subtotal = parse_amount(totales.get('subtotal') or totales.get('subtotal_sin_iva', 0))
                    # Permitir diferencia de hasta 0.5% por redondeo
                    if subtotal > 0 and abs(items_total - subtotal) > (subtotal * 0.005):
                        validation_errors.append("Incoherencia entre items y subtotal")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error validando items vs subtotal: {e}")
                    pass
        
        elif doc_type == DocumentType.RECIBO:
            structured = data.get('structured_data', {})
            
            if not structured.get('monto'):
                validation_errors.append("Falta monto en recibo")
        
        # Ajustar confianza basada en errores (penalización más inteligente)
        if validation_errors:
            base_confidence = data.get('confidence', 0.8)
            
            # Penalizar más los errores críticos
            critical_penalty = sum(0.15 for error in validation_errors if 'críticos' in error.lower())
            important_penalty = sum(0.08 for error in validation_errors if 'importantes' in error.lower())
            coherence_penalty = sum(0.05 for error in validation_errors if 'incoherencia' in error.lower() or 'formato' in error.lower())
            other_penalty = sum(0.03 for error in validation_errors if 'críticos' not in error.lower() and 'importantes' not in error.lower() and 'incoherencia' not in error.lower() and 'formato' not in error.lower())
            
            total_penalty = critical_penalty + important_penalty + coherence_penalty + other_penalty
            data['confidence'] = max(0.0, base_confidence - total_penalty)
            data['validation_errors'] = validation_errors
            data['validation_score'] = 1.0 - total_penalty  # Score de validación (0-1)
        else:
            # Bonificar si no hay errores y tiene campos completos
            base_confidence = data.get('confidence', 0.8)
            if doc_type == DocumentType.FACTURA:
                structured = data.get('structured_data', {})
                # Contar campos completados
                fields_count = 0
                total_fields = 0
                
                if structured.get('numero_factura'): fields_count += 1
                total_fields += 1
                if structured.get('fecha_emision'): fields_count += 1
                total_fields += 1
                if structured.get('emisor', {}).get('razon_social'): fields_count += 1
                total_fields += 1
                if structured.get('emisor', {}).get('cuit'): fields_count += 1
                total_fields += 1
                if structured.get('totales', {}).get('total'): fields_count += 1
                total_fields += 1
                if structured.get('items') and len(structured.get('items', [])) > 0: fields_count += 1
                total_fields += 1
                
                # Bonificar si tiene más del 80% de campos críticos
                if fields_count / total_fields >= 0.8:
                    data['confidence'] = min(1.0, base_confidence + 0.1)
                    data['validation_score'] = 1.0
                else:
                    data['validation_score'] = fields_count / total_fields
        
        return data
    
    async def _fallback_extraction(self, text: str) -> ExtractedData:
        """Fallback mejorado usando regex y spaCy"""
        
        # Detectar tipo de documento primero
        doc_type = self._detect_document_type(text)
        
        # Extracción mejorada con regex
        basic_data = self._extract_with_regex(text)
        
        # Intentar usar spaCy si está disponible
        spacy_entities = {}
        if self.nlp:
            try:
                doc = self.nlp(text)
                spacy_entities = {
                    'personas': list(set([ent.text for ent in doc.ents if ent.label_ == 'PER'])),
                    'organizaciones': list(set([ent.text for ent in doc.ents if ent.label_ == 'ORG'])),
                    'lugares': list(set([ent.text for ent in doc.ents if ent.label_ == 'LOC'])),
                    'fechas': list(set([ent.text for ent in doc.ents if ent.label_ == 'DATE'])),
                    'dinero': list(set([ent.text for ent in doc.ents if ent.label_ == 'MONEY']))
                }
            except:
                pass
        
        # Estructurar datos básicos para facturas
        if doc_type == DocumentType.FACTURA:
            structured = {
                'numero_factura': basic_data.get('numero_factura'),
                'punto_venta': basic_data.get('punto_venta'),
                'fecha_emision': basic_data.get('fecha', [None])[0] if isinstance(basic_data.get('fecha'), list) else basic_data.get('fecha'),
                'cae': basic_data.get('cae'),
                'emisor': {
                    'cuit': basic_data.get('cuit', [None])[0] if isinstance(basic_data.get('cuit'), list) else basic_data.get('cuit'),
                    'razon_social': spacy_entities.get('organizaciones', [None])[0] if spacy_entities.get('organizaciones') else None
                },
                'totales': {
                    'total': basic_data.get('monto', [None])[0] if isinstance(basic_data.get('monto'), list) else basic_data.get('monto')
                }
            }
            # Limpiar None values
            structured = {k: v for k, v in structured.items() if v is not None}
            if structured.get('emisor'):
                structured['emisor'] = {k: v for k, v in structured['emisor'].items() if v is not None}
            if structured.get('totales'):
                structured['totales'] = {k: v for k, v in structured['totales'].items() if v is not None}
        else:
            structured = basic_data
        
        # Calcular confianza basada en datos encontrados
        confidence = 0.4  # Base para fallback
        if doc_type == DocumentType.FACTURA:
            if structured.get('numero_factura'):
                confidence += 0.1
            if structured.get('emisor', {}).get('cuit'):
                confidence += 0.1
            if structured.get('totales', {}).get('total'):
                confidence += 0.1
            if structured.get('fecha_emision'):
                confidence += 0.1
        else:
            if basic_data:
                confidence += 0.2
        
        return ExtractedData(
            document_type=doc_type,
            confidence=min(0.7, confidence),  # Máximo 0.7 para fallback
            entities=spacy_entities,
            structured_data=structured,
            metadata={
                'extraction_method': 'regex_spacy_fallback',
                'llm_used': False,
                'spacy_used': self.nlp is not None,
                'validation_passed': False,
                'fields_found': len([k for k, v in structured.items() if v]) if isinstance(structured, dict) else 0
            }
        )
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """Extracción mejorada con regex para facturas"""
        
        extracted = {}
        
        # Patrones mejorados para facturas argentinas
        patterns = {
            # Fechas (múltiples formatos)
            'fecha': [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            ],
            # Período facturado
            'periodo_facturado_desde': [
                r'(Período\s+Facturado\s+Desde[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
                r'(Período\s+Fact\.?\s+Desde[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
            ],
            'periodo_facturado_hasta': [
                r'(Hasta[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',  # Buscar "Hasta" después de "Desde"
                r'(Período\s+Facturado\s+Hasta[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
            ],
            # Montos (múltiples formatos argentinos)
            'monto': [
                r'(\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # $1.234,56
                r'(\$\s?\d+(?:,\d{2})?)',  # $60000,00 o $1234,56
                r'(USD\s?\d+(?:\.\d{3})*(?:,\d{2})?)',  # USD 1.234,56
                r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:pesos|ARS))',  # 1.234,56 pesos
                r'(\d{5,}(?:,\d{2})?)',  # 60000,00 (sin punto de miles)
            ],
            # CUITs (múltiples formatos)
            'cuit': [
                r'(\d{2}-?\d{8}-?\d{1})',  # 20-12345678-9
                r'(CUIT[:\s]*\d{2}-?\d{8}-?\d{1})',  # CUIT: 20-12345678-9
                r'(C\.U\.I\.T\.\s*\d{2}-?\d{8}-?\d{1})',  # C.U.I.T. 20-12345678-9
            ],
            # Número de factura
            'numero_factura': [
                r'(FACTURA\s*N[º°]?\s*:?\s*(\d{4,5}-?\d{6,8}))',
                r'(\d{4,5}-?\d{6,8})',  # 0001-00001234
                r'(COMPROBANTE\s*N[º°]?\s*:?\s*(\d{4,5}-?\d{6,8}))',
            ],
            # Punto de venta (mejorado)
            'punto_venta': [
                r'(PTO\.?\s*VENTA[:\s]*(\d{4,5}))',
                r'(P\.V\.\s*:?\s*(\d{4,5}))',
                r'(Punto\s+de\s+Venta[:\s]*(\d{4,5}))',
            ],
            # CAE (Código de Autorización Electrónico) - mejorado para capturar formatos como "CAE N°: 75403938202167"
            'cae': [
                r'(CAE\s*N[º°]?\s*:?\s*(\d{14}))',
                r'(CAE[:\s]*(\d{14}))',
                r'(C\.A\.E\.\s*N[º°]?\s*:?\s*(\d{14}))',
                r'(C\.A\.E\.\s*:?\s*(\d{14}))',
                r'(Código\s+de\s+Autorización[:\s]*(\d{14}))',
            ],
            # Fecha de vencimiento CAE - mejorado para capturar "Fecha de Vto. de CAE: 17/10/2025"
            'cae_vencimiento': [
                r'(Fecha\s+de\s+Vto\.?\s+de\s+CAE[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
                r'(CAE\s+Vto\.?\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
                r'(Vencimiento\s+CAE[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',
            ],
            # Condición IVA
            'condicion_iva': [
                r'(Responsable\s+Inscripto)',
                r'(Responsable\s+No\s+Inscripto)',
                r'(Exento)',
                r'(Monotributista)',
                r'(Consumidor\s+Final)',
            ],
            # Alícuotas IVA
            'alicuota_iva': [
                r'(IVA\s+21%)',
                r'(IVA\s+10\.5%)',
                r'(IVA\s+27%)',
                r'(21\s*%)',
                r'(10\.5\s*%)',
                r'(27\s*%)',
            ],
            # Email
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            # Teléfono
            'telefono': [
                r'(\+?54\s?9?\d{2,4}\s?\d{6,8})',
                r'(\(?\d{2,4}\)?\s?\d{6,8})',
            ],
            # Código postal
            'codigo_postal': [
                r'(CP[:\s]*(\d{4,8}))',
                r'(C\.P\.\s*:?\s*(\d{4,8}))',
            ],
            # Ingresos Brutos
            'ingresos_brutos': [
                r'(Ing\.?\s*Brutos[:\s]*(\d{2}-?\d{8}-?\d{1}))',
                r'(I\.B\.\s*:?\s*(\d{2}-?\d{8}-?\d{1}))',
                r'(Ingresos\s+Brutos[:\s]*(\d+))',  # También puede ser solo número
            ],
            # Código de comprobante
            'codigo_comprobante': [
                r'(COD\.?\s*:?\s*(\d{3}))',
                r'(Código[:\s]*(\d{3}))',
                r'(Cód\.?\s*:?\s*(\d{3}))',
            ],
            # Descripción adicional (texto entre comillas o en cursiva)
            'descripcion_adicional': [
                r'("([^"]+)")',  # Texto entre comillas dobles
                r'(\'([^\']+)\')',  # Texto entre comillas simples
                r'((?:Desarrollo|Servicio|Producto)[^\.]+)',  # Texto que empieza con palabras clave
            ],
        }
        
        for key, pattern_list in patterns.items():
            if isinstance(pattern_list, str):
                pattern_list = [pattern_list]
            
            all_matches = []
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Si el patrón tiene grupos de captura, tomar el último grupo
                    for match in matches:
                        if isinstance(match, tuple):
                            # Tomar el último grupo no vacío
                            value = [m for m in match if m][-1] if match else match[0]
                            all_matches.append(value)
                        else:
                            all_matches.append(match)
            
            if all_matches:
                # Eliminar duplicados manteniendo orden
                unique_matches = []
                seen = set()
                for match in all_matches:
                    if match not in seen:
                        unique_matches.append(match)
                        seen.add(match)
                
                extracted[key] = unique_matches[0] if len(unique_matches) == 1 else unique_matches
        
        return extracted
