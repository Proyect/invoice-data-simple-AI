"""
Servicio de extracción básico usando solo spaCy y regex
No requiere APIs externas
"""
import re
import spacy
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasicExtractionService:
    """Servicio de extracción de datos usando spaCy y regex"""
    
    def __init__(self):
        """Inicializar el servicio"""
        try:
            self.nlp = spacy.load("es_core_news_sm")
            logger.info("Modelo de spaCy cargado correctamente")
        except Exception as e:
            logger.error(f"Error cargando modelo de spaCy: {e}")
            self.nlp = None
    
    def extract_data(self, text: str, document_type: str = "factura") -> Dict[str, Any]:
        """
        Extraer datos estructurados del texto
        
        Args:
            text: Texto extraído por OCR
            document_type: Tipo de documento (factura, recibo, etc.)
        
        Returns:
            Diccionario con datos extraídos
        """
        if not text:
            return {"error": "No hay texto para procesar"}
        
        try:
            # Detectar tipo de documento si no se especifica
            if not document_type:
                document_type = self._detect_document_type(text)
            
            # Extraer datos según el tipo de documento
            if document_type.lower() in ["factura", "invoice"]:
                return self._extract_invoice_data(text)
            elif document_type.lower() in ["recibo", "receipt"]:
                return self._extract_receipt_data(text)
            else:
                return self._extract_generic_data(text)
                
        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}")
            return {"error": str(e)}
    
    def _detect_document_type(self, text: str) -> str:
        """Detectar el tipo de documento"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["factura", "invoice", "fact.", "fac."]):
            return "factura"
        elif any(word in text_lower for word in ["recibo", "receipt", "comprobante"]):
            return "recibo"
        elif any(word in text_lower for word in ["boleta", "ticket"]):
            return "boleta"
        else:
            return "documento"
    
    def _extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extraer datos de una factura"""
        data = {
            "tipo_documento": "factura",
            "numero_factura": self._extract_invoice_number(text),
            "fecha": self._extract_date(text),
            "emisor": self._extract_company_name(text),
            "receptor": self._extract_customer_name(text),
            "montos": self._extract_amounts(text),
            "items": self._extract_items(text),
            "totales": self._extract_totals(text),
            "cuit": self._extract_cuit(text),
            "condicion_iva": self._extract_iva_condition(text),
        }
        
        return {k: v for k, v in data.items() if v}  # Remover campos vacíos
    
    def _extract_receipt_data(self, text: str) -> Dict[str, Any]:
        """Extraer datos de un recibo"""
        data = {
            "tipo_documento": "recibo",
            "numero_recibo": self._extract_invoice_number(text),
            "fecha": self._extract_date(text),
            "emisor": self._extract_company_name(text),
            "receptor": self._extract_customer_name(text),
            "monto": self._extract_total_amount(text),
            "concepto": self._extract_concept(text),
        }
        
        return {k: v for k, v in data.items() if v}
    
    def _extract_generic_data(self, text: str) -> Dict[str, Any]:
        """Extraer datos genéricos de cualquier documento"""
        data = {
            "fechas": self._extract_dates(text),
            "montos": self._extract_amounts(text),
            "emails": self._extract_emails(text),
            "telefonos": self._extract_phones(text),
            "entidades": self._extract_entities(text),
        }
        
        return {k: v for k, v in data.items() if v}
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extraer número de factura"""
        patterns = [
            r'(?:factura|invoice|fact\.|fac\.)\s*(?:n[°º]?|#|num\.?|número)?\s*[:\-]?\s*([A-Z]?\d{4,}[\-/]?\d*)',
            r'(?:n[°º]|#)\s*(\d{4,}[\-/]?\d*)',
            r'(\d{4}-\d{8})',  # Formato típico argentino
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extraer fecha principal del documento"""
        dates = self._extract_dates(text)
        return dates[0] if dates else None
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extraer todas las fechas del texto"""
        dates = []
        patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY o DD-MM-YYYY
            r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',  # DD de mes de YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))  # Remover duplicados
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extraer nombre de empresa emisora"""
        # Buscar en las primeras líneas
        lines = text.split('\n')[:10]
        
        # Buscar después de palabras clave
        for line in lines:
            if any(word in line.lower() for word in ['razón social', 'empresa', 'emisor']):
                # La siguiente línea suele ser el nombre
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    return lines[idx + 1].strip()
        
        # Usar spaCy para encontrar organizaciones
        if self.nlp:
            doc = self.nlp(' '.join(lines))
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs:
                return orgs[0]
        
        return None
    
    def _extract_customer_name(self, text: str) -> Optional[str]:
        """Extraer nombre del cliente/receptor"""
        patterns = [
            r'(?:cliente|receptor|señor(?:es)?|sra?\.|destinatario)[:\s]+([^\n]+)',
            r'(?:a nombre de|para)[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extraer todos los montos del documento"""
        amounts = []
        patterns = [
            r'\$\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # $1.234,56 o $1,234.56
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:pesos|dolares|usd|ars)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amounts.append({
                    "valor": match,
                    "moneda": "ARS" if "peso" in text.lower() else "USD"
                })
        
        return amounts
    
    def _extract_total_amount(self, text: str) -> Optional[str]:
        """Extraer monto total"""
        patterns = [
            r'(?:total|importe total|monto total)[:\s]*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Si no se encuentra, usar el último monto grande
        amounts = self._extract_amounts(text)
        if amounts:
            return amounts[-1]["valor"]
        
        return None
    
    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extraer items/productos de la factura"""
        items = []
        # Buscar líneas con patrón: cantidad - descripción - precio
        pattern = r'(\d+)\s+([A-Za-z\s]+)\s+\$?\s*(\d+[.,]\d{2})'
        matches = re.findall(pattern, text)
        
        for match in matches:
            items.append({
                "cantidad": match[0],
                "descripcion": match[1].strip(),
                "precio": match[2]
            })
        
        return items
    
    def _extract_totals(self, text: str) -> Dict[str, str]:
        """Extraer totales (subtotal, IVA, total)"""
        totals = {}
        
        patterns = {
            "subtotal": r'(?:subtotal)[:\s]*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            "iva": r'(?:iva|i\.v\.a\.)[:\s]*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            "total": r'(?:total)[:\s]*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                totals[key] = match.group(1)
        
        return totals
    
    def _extract_cuit(self, text: str) -> Optional[str]:
        """Extraer CUIT/CUIL"""
        pattern = r'(?:cuit|cuil)[:\s]*(\d{2}-\d{8}-\d{1})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar formato sin guiones
        pattern = r'(?:cuit|cuil)[:\s]*(\d{11})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cuit = match.group(1)
            return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
        
        return None
    
    def _extract_iva_condition(self, text: str) -> Optional[str]:
        """Extraer condición ante IVA"""
        patterns = [
            r'(responsable inscripto)',
            r'(monotributo)',
            r'(exento)',
            r'(consumidor final)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).title()
        
        return None
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extraer emails"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extraer teléfonos"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{3,4}\)\s*\d{6,8}',
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))
    
    def _extract_concept(self, text: str) -> Optional[str]:
        """Extraer concepto del recibo"""
        patterns = [
            r'(?:concepto|por)[:\s]+([^\n]+)',
            r'(?:pago de|abono de)[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extraer entidades nombradas usando spaCy"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text[:1000])  # Limitar a primeros 1000 caracteres
        
        entities = {
            "personas": [],
            "organizaciones": [],
            "lugares": [],
            "fechas": [],
            "dinero": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "PER":
                entities["personas"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizaciones"].append(ent.text)
            elif ent.label_ == "LOC":
                entities["lugares"].append(ent.text)
            elif ent.label_ in ["DATE", "TIME"]:
                entities["fechas"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["dinero"].append(ent.text)
        
        # Remover duplicados
        return {k: list(set(v)) for k, v in entities.items() if v}

# Instancia global del servicio
_basic_extraction_service = None

def get_basic_extraction_service() -> BasicExtractionService:
    """Obtener instancia del servicio de extracción básico"""
    global _basic_extraction_service
    if _basic_extraction_service is None:
        _basic_extraction_service = BasicExtractionService()
    return _basic_extraction_service

