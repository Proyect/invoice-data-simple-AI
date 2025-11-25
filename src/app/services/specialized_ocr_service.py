"""
Servicio OCR especializado para campos pequeños como CAE, CUIT, etc.
Usa técnicas avanzadas gratuitas para máxima precisión
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class SpecializedOCRService:
    """
    Servicio OCR especializado para campos pequeños y críticos
    """
    
    def __init__(self):
        # Configuraciones optimizadas para diferentes tipos de texto
        self.configs = {
            'numbers_only': r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            'alphanumeric': r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            'small_text': r'--oem 3 --psm 6',
            'single_word': r'--oem 3 --psm 7',
            'single_line': r'--oem 3 --psm 8',
            'single_char': r'--oem 3 --psm 10'
        }
        
        # Diccionarios para corrección post-OCR
        self.correction_dict = {
            'cae': {
                'common_errors': {
                    'O': '0', 'I': '1', 'l': '1', 'S': '5', 'B': '8',
                    'G': '6', 'Z': '2', 'T': '7'
                },
                'expected_length': 14,
                'pattern': r'^\d{14}$'
            },
            'cuit': {
                'common_errors': {
                    'O': '0', 'I': '1', 'l': '1', 'S': '5', 'B': '8',
                    'G': '6', 'Z': '2', 'T': '7'
                },
                'expected_length': 11,
                'pattern': r'^\d{11}$'
            },
            'amount': {
                'common_errors': {
                    'O': '0', 'I': '1', 'l': '1', 'S': '5', 'B': '8',
                    'G': '6', 'Z': '2', 'T': '7'
                },
                'pattern': r'^\d+[.,]\d{2}$'
            }
        }
    
    def extract_small_field(self, image_path: str, field_type: str = 'numbers_only', 
                          region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Extraer campo pequeño con máxima precisión
        
        Args:
            image_path: Ruta de la imagen
            field_type: Tipo de campo (numbers_only, alphanumeric, etc.)
            region: Región específica (x, y, width, height) si se conoce
            
        Returns:
            str: Texto extraído y corregido
        """
        try:
            logger.info(f"Extrayendo campo pequeño: {field_type}")
            
            # Cargar imagen
            image = Image.open(image_path)
            
            # Si se especifica región, recortar
            if region:
                x, y, w, h = region
                image = image.crop((x, y, x + w, y + h))
                logger.info(f"Recortando región: {region}")
            
            # Aplicar múltiples técnicas de preprocesamiento
            processed_images = self._create_multiple_processed_images(image)
            
            # Intentar extracción con cada imagen procesada
            results = []
            for i, processed_img in enumerate(processed_images):
                for config_name, config in self.configs.items():
                    try:
                        text = pytesseract.image_to_string(processed_img, config=config).strip()
                        if text:
                            # Aplicar corrección post-OCR
                            corrected_text = self._correct_text(text, field_type)
                            if corrected_text:
                                confidence = self._calculate_confidence(corrected_text, field_type)
                                results.append({
                                    'text': corrected_text,
                                    'confidence': confidence,
                                    'config': config_name,
                                    'processing': i
                                })
                                logger.info(f"Resultado {i}-{config_name}: {corrected_text} (confianza: {confidence:.2f})")
                    except Exception as e:
                        logger.warning(f"Error con configuración {config_name}: {e}")
                        continue
            
            # Seleccionar mejor resultado
            if results:
                best_result = max(results, key=lambda x: x['confidence'])
                logger.info(f"Mejor resultado: {best_result['text']} (confianza: {best_result['confidence']:.2f})")
                return best_result['text']
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extrayendo campo pequeño: {e}")
            return ""
    
    def _create_multiple_processed_images(self, image: Image.Image) -> List[Image.Image]:
        """
        Crear múltiples versiones procesadas de la imagen para máxima precisión
        """
        processed_images = []
        
        try:
            # Imagen original
            processed_images.append(image.copy())
            
            # 1. Escala de grises
            gray_image = image.convert('L')
            processed_images.append(gray_image)
            
            # 2. Alto contraste
            enhancer = ImageEnhance.Contrast(gray_image)
            high_contrast = enhancer.enhance(3.0)
            processed_images.append(high_contrast)
            
            # 3. Imagen más grande (escalada)
            width, height = image.size
            if width < 800:  # Solo escalar si es pequeña
                scale_factor = 800 / width
                new_size = (int(width * scale_factor), int(height * scale_factor))
                scaled = image.resize(new_size, Image.LANCZOS)
                processed_images.append(scaled)
            
            # 4. Filtro de nitidez
            sharp_image = gray_image.filter(ImageFilter.SHARPEN)
            processed_images.append(sharp_image)
            
            # 5. Combinación de nitidez y contraste
            sharp_contrast = ImageEnhance.Contrast(sharp_image).enhance(2.0)
            processed_images.append(sharp_contrast)
            
            # 6. Procesamiento con OpenCV para mejor calidad
            cv_images = self._create_cv_processed_images(image)
            processed_images.extend(cv_images)
            
            logger.info(f"Creadas {len(processed_images)} imágenes procesadas")
            return processed_images
            
        except Exception as e:
            logger.error(f"Error creando imágenes procesadas: {e}")
            return [image]
    
    def _create_cv_processed_images(self, image: Image.Image) -> List[Image.Image]:
        """
        Crear imágenes procesadas con OpenCV para mejor calidad
        """
        cv_images = []
        
        try:
            # Convertir PIL a OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 1. Escala de grises
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            cv_images.append(Image.fromarray(gray))
            
            # 2. Umbral adaptativo
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            cv_images.append(Image.fromarray(thresh))
            
            # 3. Filtro gaussiano + umbral
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            thresh_blur = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            cv_images.append(Image.fromarray(thresh_blur))
            
            # 4. Morfología para limpiar
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cv_images.append(Image.fromarray(cleaned))
            
            # 5. Dilatación para engrosar texto fino
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            cv_images.append(Image.fromarray(dilated))
            
            # 6. Erosión para afinar texto grueso
            eroded = cv2.erode(thresh, kernel, iterations=1)
            cv_images.append(Image.fromarray(eroded))
            
            logger.info(f"Creadas {len(cv_images)} imágenes con OpenCV")
            
        except Exception as e:
            logger.error(f"Error procesando con OpenCV: {e}")
        
        return cv_images
    
    def _correct_text(self, text: str, field_type: str) -> str:
        """
        Corregir texto extraído basado en errores comunes de OCR
        """
        if not text:
            return ""
        
        # Limpiar texto
        cleaned_text = re.sub(r'[^\w\d]', '', text)
        
        # Obtener configuración de corrección
        correction_config = self.correction_dict.get(field_type, {})
        common_errors = correction_config.get('common_errors', {})
        expected_length = correction_config.get('expected_length')
        pattern = correction_config.get('pattern')
        
        # Aplicar correcciones comunes
        corrected_text = cleaned_text
        for wrong, right in common_errors.items():
            corrected_text = corrected_text.replace(wrong, right)
        
        # Validar longitud esperada
        if expected_length and len(corrected_text) != expected_length:
            logger.warning(f"Longitud incorrecta: esperado {expected_length}, obtenido {len(corrected_text)}")
            # Intentar ajustar agregando/quitando dígitos comunes
            if len(corrected_text) < expected_length:
                # Agregar ceros al final
                corrected_text = corrected_text.ljust(expected_length, '0')
            elif len(corrected_text) > expected_length:
                # Truncar al largo esperado
                corrected_text = corrected_text[:expected_length]
        
        # Validar patrón
        if pattern and not re.match(pattern, corrected_text):
            logger.warning(f"Patrón no coincide: {corrected_text}")
            return ""
        
        return corrected_text
    
    def _calculate_confidence(self, text: str, field_type: str) -> float:
        """
        Calcular confianza basada en el tipo de campo
        """
        if not text:
            return 0.0
        
        confidence = 0.5  # Base
        
        # Bonificación por longitud correcta
        correction_config = self.correction_dict.get(field_type, {})
        expected_length = correction_config.get('expected_length')
        
        if expected_length and len(text) == expected_length:
            confidence += 0.3
        
        # Bonificación por patrón correcto
        pattern = correction_config.get('pattern')
        if pattern and re.match(pattern, text):
            confidence += 0.2
        
        # Bonificación por no tener caracteres extraños
        if re.match(r'^[\d]+$', text):  # Solo números
            confidence += 0.1
        elif re.match(r'^[\d\-]+$', text):  # Números y guiones
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def extract_cae_from_invoice(self, image_path: str) -> Dict[str, Any]:
        """
        Extraer específicamente el CAE de una factura
        """
        try:
            logger.info("Extrayendo CAE de factura")
            
            # Cargar imagen
            image = Image.open(image_path)
            width, height = image.size
            
            # Regiones comunes donde aparece el CAE (parte inferior)
            cae_regions = [
                # Región inferior derecha (más común)
                (width//2, height//2, width//2, height//2),
                # Región inferior completa
                (0, height*3//4, width, height//4),
                # Región derecha inferior
                (width*2//3, height*2//3, width//3, height//3),
            ]
            
            results = []
            
            # Intentar en cada región
            for i, region in enumerate(cae_regions):
                x, y, w, h = region
                cropped = image.crop((x, y, x + w, y + h))
                
                # Extraer texto de la región
                text = self.extract_small_field_from_image(cropped, 'cae')
                
                if text and len(text) >= 10:  # CAE debe ser al menos 10 dígitos
                    confidence = self._calculate_confidence(text, 'cae')
                    results.append({
                        'cae': text,
                        'confidence': confidence,
                        'region': i,
                        'position': (x, y, w, h)
                    })
                    logger.info(f"CAE encontrado en región {i}: {text} (confianza: {confidence:.2f})")
            
            # También buscar en toda la imagen con patrones específicos
            full_image_result = self._search_cae_patterns(image)
            if full_image_result:
                results.append(full_image_result)
            
            # Seleccionar mejor resultado
            if results:
                best_result = max(results, key=lambda x: x['confidence'])
                return {
                    'cae_number': best_result['cae'],
                    'confidence': best_result['confidence'],
                    'found_in_region': best_result['region'],
                    'all_results': results
                }
            
            return {
                'cae_number': '',
                'confidence': 0.0,
                'found_in_region': -1,
                'all_results': []
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo CAE: {e}")
            return {
                'cae_number': '',
                'confidence': 0.0,
                'found_in_region': -1,
                'all_results': [],
                'error': str(e)
            }
    
    def extract_small_field_from_image(self, image: Image.Image, field_type: str) -> str:
        """
        Extraer campo pequeño directamente de una imagen PIL
        """
        try:
            # Aplicar múltiples técnicas de preprocesamiento
            processed_images = self._create_multiple_processed_images(image)
            
            results = []
            for i, processed_img in enumerate(processed_images):
                for config_name, config in self.configs.items():
                    try:
                        text = pytesseract.image_to_string(processed_img, config=config).strip()
                        if text:
                            corrected_text = self._correct_text(text, field_type)
                            if corrected_text:
                                confidence = self._calculate_confidence(corrected_text, field_type)
                                results.append({
                                    'text': corrected_text,
                                    'confidence': confidence
                                })
                    except Exception:
                        continue
            
            if results:
                best_result = max(results, key=lambda x: x['confidence'])
                return best_result['text']
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extrayendo campo: {e}")
            return ""
    
    def _search_cae_patterns(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Buscar patrones específicos de CAE en la imagen
        """
        try:
            # Extraer todo el texto de la imagen
            full_text = pytesseract.image_to_string(image, lang='spa')
            
            # Buscar patrones de CAE
            cae_patterns = [
                r'CAE\s*N°?\s*:\s*(\d{14})',
                r'CAE\s*N°?\s*:\s*(\d{13,15})',
                r'CAE\s*:\s*(\d{14})',
                r'C\.A\.E\.\s*N°?\s*:\s*(\d{14})',
                r'Código\s+de\s+Autorización\s+Electrónica\s*:\s*(\d{14})'
            ]
            
            for pattern in cae_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    cae = matches[0]
                    if len(cae) == 14:  # CAE debe tener 14 dígitos
                        confidence = self._calculate_confidence(cae, 'cae')
                        return {
                            'cae': cae,
                            'confidence': confidence,
                            'region': 'full_text',
                            'position': 'pattern_match'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando patrones CAE: {e}")
            return None










