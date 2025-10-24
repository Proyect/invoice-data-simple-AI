import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from google.cloud import vision
import pytesseract
from PIL import Image
import boto3
import cv2
import numpy as np
import os
from ..core.config import settings

logger = logging.getLogger(__name__)

class DocumentComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

@dataclass
class OCRResult:
    text: str
    confidence: float
    provider: str
    cost: float
    processing_time: float
    metadata: Dict[str, Any]

class OptimalOCRService:
    """
    Servicio OCR optimizado que combina múltiples estrategias
    """
    
    def __init__(self):
        # Inicializar clientes
        self.google_client = None
        self.aws_textract = None
        
        # Configuraciones
        self.daily_google_limit = settings.GOOGLE_VISION_DAILY_LIMIT
        self.daily_aws_limit = settings.AWS_TEXTRACT_DAILY_LIMIT
        self.google_used_today = 0
        self.aws_used_today = 0
        
        # Umbrales de decisión
        self.complexity_thresholds = {
            DocumentComplexity.SIMPLE: 0.3,
            DocumentComplexity.MEDIUM: 0.6,
            DocumentComplexity.COMPLEX: 0.8
        }
        
        # Inicializar clientes si están configurados
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes de cloud OCR si están configurados"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.google_client = vision.ImageAnnotatorClient()
                logger.info("Google Vision API inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar Google Vision API: {e}")
        
        try:
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                self.aws_textract = boto3.client(
                    'textract',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info("AWS Textract inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar AWS Textract: {e}")
    
    def extract_text(self, image_path: str, method: str = "auto") -> str:
        """
        Método síncrono para extraer texto (compatibilidad con código existente)
        """
        try:
            logger.info(f"Extrayendo texto de: {image_path} con método: {method}")
            # Para compatibilidad, usar Tesseract directamente
            if method == "auto" or method == "tesseract":
                result = self._extract_with_tesseract(image_path)
                logger.info(f"Resultado Tesseract: {result[:100]}...")
                return result
            else:
                # Para otros métodos, usar la estrategia óptima
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.extract_text_optimal(image_path))
                    logger.info(f"Resultado óptimo: {result.text[:100]}...")
                    return result.text
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Error extrayendo texto: {e}")
            return ""

    def _extract_with_tesseract(self, image_path: str) -> str:
        """
        Extrae texto usando Tesseract OCR con preprocesamiento de alta precisión
        """
        try:
            logger.info(f"Procesando archivo con Tesseract de alta precisión: {image_path}")
            
            # Verificar si es PDF
            if image_path.lower().endswith('.pdf'):
                logger.info("Archivo es PDF, convirtiendo a imagen...")
                # Convertir PDF a imagen usando pdf2image con alta resolución
                from pdf2image import convert_from_path
                images = convert_from_path(image_path, dpi=300)  # Alta resolución
                if images:
                    logger.info(f"PDF convertido a {len(images)} imágenes")
                    # Usar la primera página
                    image = images[0]
                    # Preprocesar imagen para mejor OCR
                    processed_image = self._preprocess_image_for_ocr(image)
                    # OCR con configuración optimizada
                    text = self._extract_text_with_high_precision(processed_image)
                    logger.info(f"Texto extraído del PDF: {text[:100]}...")
                    return text
                else:
                    logger.warning("No se pudieron extraer imágenes del PDF")
                    return ""
            else:
                logger.info("Archivo es imagen, procesando directamente...")
                # Es una imagen, procesar directamente
                image = Image.open(image_path)
                # Preprocesar imagen para mejor OCR
                processed_image = self._preprocess_image_for_ocr(image)
                # OCR con configuración optimizada
                text = self._extract_text_with_high_precision(processed_image)
                logger.info(f"Texto extraído de imagen: {text[:100]}...")
                return text
        except Exception as e:
            logger.error(f"Error con Tesseract: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ""
    
    def _preprocess_image_for_ocr(self, image) -> Image.Image:
        """
        Preprocesa imagen para mejorar la precisión del OCR
        """
        try:
            import numpy as np
            
            # Convertir PIL a numpy array
            img_array = np.array(image)
            
            # Convertir a escala de grises si es necesario
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Aplicar filtros para mejorar el contraste
            # 1. Aplicar filtro gaussiano para reducir ruido
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
            
            # 2. Aplicar umbral adaptativo para mejorar el contraste
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # 3. Operaciones morfológicas para limpiar la imagen
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 4. Redimensionar para mejorar la resolución (si es necesario)
            height, width = cleaned.shape
            if height < 1000:  # Si la imagen es muy pequeña
                scale_factor = 1000 / height
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                cleaned = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Convertir de vuelta a PIL Image
            processed_image = Image.fromarray(cleaned)
            
            logger.info("Imagen preprocesada para OCR de alta precisión")
            return processed_image
            
        except Exception as e:
            logger.warning(f"Error en preprocesamiento, usando imagen original: {e}")
            return image
    
    def _extract_text_with_high_precision(self, image) -> str:
        """
        Extrae texto con configuración de alta precisión
        """
        try:
            # Configuración optimizada para Tesseract
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñü.,:;()$-/ '
            
            # Intentar múltiples configuraciones para máxima precisión
            configs = [
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñü.,:;()$-/ ',
                r'--oem 3 --psm 4',
                r'--oem 3 --psm 6',
                r'--oem 3 --psm 8',
                r'--oem 1 --psm 6'
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    # Extraer texto con confianza
                    text = pytesseract.image_to_string(image, lang='spa', config=config)
                    
                    # Obtener datos de confianza
                    data = pytesseract.image_to_data(image, lang='spa', config=config, output_type=pytesseract.Output.DICT)
                    
                    # Calcular confianza promedio
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Si esta configuración da mejor resultado, guardarla
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_text = text
                        
                    logger.info(f"Config {config[:20]}... - Confianza: {avg_confidence:.1f}%")
                    
                except Exception as e:
                    logger.warning(f"Error con configuración {config[:20]}: {e}")
                    continue
            
            logger.info(f"Mejor configuración seleccionada - Confianza: {best_confidence:.1f}%")
            return best_text
            
        except Exception as e:
            logger.error(f"Error en extracción de alta precisión: {e}")
            # Fallback a configuración básica
            return pytesseract.image_to_string(image, lang='spa')

    async def extract_text_optimal(self, image_path: str, document_type: str = None) -> OCRResult:
        """
        Extrae texto usando la estrategia óptima
        """
        import time
        start_time = time.time()
        
        try:
            # Paso 1: Análisis rápido de complejidad
            complexity = await self._analyze_document_complexity(image_path)
            
            # Paso 2: Decidir estrategia óptima
            strategy = self._select_optimal_strategy(complexity, document_type)
            
            # Paso 3: Ejecutar estrategia seleccionada
            result = await self._execute_strategy(strategy, image_path)
            
            # Paso 4: Validar y mejorar resultado
            validated_result = await self._validate_and_improve(result, image_path)
            
            import time
            processing_time = time.time() - start_time
            validated_result.processing_time = processing_time
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error en extracción óptima: {e}")
            # Fallback a Tesseract
            return await self._fallback_tesseract(image_path, start_time)
    
    async def _analyze_document_complexity(self, image_path: str) -> DocumentComplexity:
        """
        Análisis avanzado de complejidad del documento
        """
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                return DocumentComplexity.MEDIUM
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            complexity_score = 0.0
            
            # 1. Análisis de resolución
            height, width = gray.shape
            total_pixels = height * width
            if total_pixels > 2000000:  # Más de 2MP
                complexity_score += 0.2
            
            # 2. Análisis de contraste
            contrast = np.std(gray)
            if contrast < 30:  # Bajo contraste
                complexity_score += 0.3
            
            # 3. Detección de bordes (estructuras complejas)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / total_pixels
            if edge_density > 0.1:  # Muchos bordes
                complexity_score += 0.3
            
            # 4. Detección de texto (densidad de texto)
            text_density = await self._estimate_text_density(gray)
            complexity_score += text_density * 0.2
            
            # Determinar complejidad
            if complexity_score < self.complexity_thresholds[DocumentComplexity.SIMPLE]:
                return DocumentComplexity.SIMPLE
            elif complexity_score < self.complexity_thresholds[DocumentComplexity.MEDIUM]:
                return DocumentComplexity.MEDIUM
            else:
                return DocumentComplexity.COMPLEX
                
        except Exception as e:
            logger.error(f"Error analizando complejidad: {e}")
            return DocumentComplexity.MEDIUM
    
    async def _estimate_text_density(self, gray_image) -> float:
        """
        Estima la densidad de texto en la imagen
        """
        try:
            # Usar detección de contornos para estimar densidad de texto
            # Compatible con OpenCV 3.x y 4.x
            result = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = result[0] if len(result) == 2 else result[1]
            
            total_contour_area = sum(cv2.contourArea(c) for c in contours)
            image_area = gray_image.shape[0] * gray_image.shape[1]
            
            return min(total_contour_area / image_area, 1.0)
        except:
            return 0.5  # Valor por defecto
    
    def _select_optimal_strategy(self, complexity: DocumentComplexity, document_type: str = None) -> str:
        """
        Selecciona la estrategia óptima basada en complejidad y tipo
        """
        
        # Estrategias por complejidad
        if complexity == DocumentComplexity.SIMPLE:
            return "tesseract"
        elif complexity == DocumentComplexity.MEDIUM:
            if document_type in ["factura", "recibo"]:
                return "google_vision"  # Mayor precisión para documentos financieros
            else:
                return "tesseract_with_validation"
        else:  # COMPLEX
            if document_type == "formulario":
                return "aws_textract"  # Mejor para formularios estructurados
            else:
                return "google_vision"  # Máxima precisión para documentos complejos
    
    async def _execute_strategy(self, strategy: str, image_path: str) -> OCRResult:
        """
        Ejecuta la estrategia seleccionada
        """
        
        if strategy == "tesseract":
            return await self._use_tesseract(image_path)
        elif strategy == "google_vision":
            return await self._use_google_vision(image_path)
        elif strategy == "aws_textract":
            return await self._use_aws_textract(image_path)
        elif strategy == "tesseract_with_validation":
            return await self._use_tesseract_with_validation(image_path)
        else:
            return await self._use_tesseract(image_path)
    
    async def _use_google_vision(self, image_path: str) -> OCRResult:
        """Usar Google Vision API"""
        if not self.google_client:
            logger.warning("Google Vision API no disponible, usando Tesseract")
            return await self._use_tesseract(image_path)
        
        if self.google_used_today >= self.daily_google_limit:
            logger.warning("Límite diario de Google Vision alcanzado")
            return await self._use_tesseract(image_path)
        
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.google_client.text_detection(image=image)
            
            text = ""
            if response.text_annotations:
                text = response.text_annotations[0].description
            
            self.google_used_today += 1
            
            return OCRResult(
                text=text,
                confidence=0.95,
                provider="google_vision",
                cost=0.0015,
                processing_time=0.0,  # Se calculará después
                metadata={
                    "daily_usage": self.google_used_today,
                    "detected_language": "es",
                    "text_blocks": len(response.text_annotations) if response.text_annotations else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Error con Google Vision: {e}")
            return await self._use_tesseract(image_path)
    
    async def _use_aws_textract(self, image_path: str) -> OCRResult:
        """Usar AWS Textract para formularios"""
        if not self.aws_textract:
            logger.warning("AWS Textract no disponible, usando Tesseract")
            return await self._use_tesseract(image_path)
        
        if self.aws_used_today >= self.daily_aws_limit:
            logger.warning("Límite diario de AWS Textract alcanzado")
            return await self._use_tesseract(image_path)
        
        try:
            with open(image_path, 'rb') as document:
                response = self.aws_textract.analyze_document(
                    Document={'Bytes': document.read()},
                    FeatureTypes=['TABLES', 'FORMS']
                )
            
            # Procesar respuesta de Textract
            text = self._process_textract_response(response)
            confidence = self._calculate_textract_confidence(response)
            
            self.aws_used_today += 1
            
            return OCRResult(
                text=text,
                confidence=confidence,
                provider="aws_textract",
                cost=0.0015,
                processing_time=0.0,
                metadata={
                    "daily_usage": self.aws_used_today,
                    "blocks_detected": len(response.get('Blocks', [])),
                    "forms_detected": len([b for b in response.get('Blocks', []) if b.get('BlockType') == 'KEY_VALUE_SET'])
                }
            )
            
        except Exception as e:
            logger.error(f"Error con AWS Textract: {e}")
            return await self._use_tesseract(image_path)
    
    async def _use_tesseract(self, image_path: str) -> OCRResult:
        """Usar Tesseract como fallback"""
        try:
            image = Image.open(image_path)
            
            # Configuración optimizada para español
            custom_config = r'--oem 3 --psm 6 -l spa'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Calcular confianza
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.5
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                provider="tesseract",
                cost=0.0,
                processing_time=0.0,
                metadata={
                    "words_detected": len([w for w in data['text'] if w.strip()]),
                    "avg_word_confidence": avg_confidence
                }
            )
            
        except Exception as e:
            logger.error(f"Error con Tesseract: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                provider="tesseract",
                cost=0.0,
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    async def _use_tesseract_with_validation(self, image_path: str) -> OCRResult:
        """Tesseract con validación adicional"""
        result = await self._use_tesseract(image_path)
        
        # Validaciones adicionales
        if result.confidence < settings.TESSERACT_CONFIDENCE_THRESHOLD:
            # Intentar con diferentes configuraciones
            image = Image.open(image_path)
            
            # Probar diferentes PSM (Page Segmentation Mode)
            for psm in [3, 4, 6, 8]:
                config = f'--oem 3 --psm {psm} -l spa'
                try:
                    text = pytesseract.image_to_string(image, config=config)
                    if len(text.strip()) > len(result.text.strip()):
                        result.text = text.strip()
                        result.metadata["psm_used"] = psm
                except:
                    continue
        
        return result
    
    def _process_textract_response(self, response: Dict) -> str:
        """Procesa respuesta de AWS Textract"""
        text_blocks = []
        
        for block in response.get('Blocks', []):
            if block.get('BlockType') == 'LINE':
                text_blocks.append(block.get('Text', ''))
        
        return '\n'.join(text_blocks)
    
    def _calculate_textract_confidence(self, response: Dict) -> float:
        """Calcula confianza promedio de AWS Textract"""
        confidences = []
        
        for block in response.get('Blocks', []):
            if 'Confidence' in block:
                confidences.append(block['Confidence'])
        
        return sum(confidences) / len(confidences) / 100 if confidences else 0.5
    
    async def _validate_and_improve(self, result: OCRResult, image_path: str) -> OCRResult:
        """
        Valida y mejora el resultado
        """
        
        # Validaciones básicas
        if len(result.text.strip()) < 10:
            result.metadata["warning"] = "Texto muy corto detectado"
        
        if result.confidence < 0.5:
            result.metadata["warning"] = "Baja confianza en OCR"
        
        # Mejoras de texto
        result.text = self._clean_text(result.text)
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Limpia y normaliza el texto"""
        import re
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Corregir caracteres comunes
        text = text.replace('|', 'I').replace('0', 'O')
        
        # Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    async def _fallback_tesseract(self, image_path: str, start_time: float) -> OCRResult:
        """Fallback a Tesseract en caso de error"""
        import time
        result = await self._use_tesseract(image_path)
        result.processing_time = time.time() - start_time
        result.metadata["fallback"] = True
        return result
