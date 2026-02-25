#!/usr/bin/env python3
"""
Test de Servicios OCR
=====================

Tests de servicios OCR: Tesseract, Google Vision, AWS Textract.
"""
import sys
import os
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import io

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.services.optimal_ocr_service import OptimalOCRService
from app.core.environment import get_settings


@dataclass
class OCRTestResult:
    """Resultado de test OCR"""
    provider: str
    success: bool
    text_extracted: bool = False
    confidence: Optional[float] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict] = None


class OCRServiceTester:
    """Tester para servicios OCR"""
    
    def __init__(self):
        self.settings = get_settings()
        self.test_results: list[OCRTestResult] = []
        self.test_image = self._create_test_image()
    
    def _create_test_image(self) -> bytes:
        """Crear imagen de prueba con texto"""
        # Crear imagen simple con texto
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Intentar usar una fuente, si no está disponible usar la default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "FACTURA\nN° 001-2024\nTotal: $1000.00"
        draw.text((50, 50), text, fill='black', font=font)
        
        # Convertir a bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_tesseract_ocr(self) -> OCRTestResult:
        """Testear Tesseract OCR"""
        print("🔍 Testeando Tesseract OCR...")
        
        start_time = time.time()
        
        try:
            ocr_service = OptimalOCRService()
            
            if not ocr_service.tesseract_available:
                return OCRTestResult(
                    provider="Tesseract",
                    success=False,
                    error="Tesseract no está disponible"
                )
            
            # Realizar OCR
            result = ocr_service.extract_text_from_image(self.test_image)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result and result.text:
                text_extracted = len(result.text.strip()) > 0
                confidence = result.confidence if hasattr(result, 'confidence') else None
                
                result_obj = OCRTestResult(
                    provider="Tesseract",
                    success=True,
                    text_extracted=text_extracted,
                    confidence=confidence,
                    response_time_ms=elapsed_ms,
                    details={
                        "text_length": len(result.text),
                        "text_preview": result.text[:100] if result.text else ""
                    }
                )
                
                print(f"   ✅ Tesseract funcionando ({elapsed_ms:.0f}ms)")
                print(f"      Texto extraído: {len(result.text)} caracteres")
                if confidence:
                    print(f"      Confianza: {confidence:.2f}")
                
            else:
                result_obj = OCRTestResult(
                    provider="Tesseract",
                    success=False,
                    error="No se extrajo texto"
                )
                print(f"   ⚠️  Tesseract no extrajo texto")
                
        except Exception as e:
            result_obj = OCRTestResult(
                provider="Tesseract",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error con Tesseract: {e}")
        
        self.test_results.append(result_obj)
        return result_obj
    
    def test_google_vision_ocr(self) -> OCRTestResult:
        """Testear Google Cloud Vision OCR"""
        print("🔍 Testeando Google Cloud Vision OCR...")
        
        start_time = time.time()
        
        try:
            ocr_service = OptimalOCRService()
            
            if not ocr_service.google_client:
                result_obj = OCRTestResult(
                    provider="Google Vision",
                    success=True,  # Opcional, no es error
                    error="Google Vision no configurado (opcional)"
                )
                print(f"   ⚠️  Google Vision no configurado (opcional)")
                self.test_results.append(result_obj)
                return result_obj
            
            # Realizar OCR
            result = ocr_service.extract_text_from_image(self.test_image, provider="google_vision")
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result and result.text:
                text_extracted = len(result.text.strip()) > 0
                confidence = result.confidence if hasattr(result, 'confidence') else None
                
                result_obj = OCRTestResult(
                    provider="Google Vision",
                    success=True,
                    text_extracted=text_extracted,
                    confidence=confidence,
                    response_time_ms=elapsed_ms,
                    details={
                        "text_length": len(result.text),
                        "text_preview": result.text[:100] if result.text else ""
                    }
                )
                
                print(f"   ✅ Google Vision funcionando ({elapsed_ms:.0f}ms)")
                print(f"      Texto extraído: {len(result.text)} caracteres")
                if confidence:
                    print(f"      Confianza: {confidence:.2f}")
                
            else:
                result_obj = OCRTestResult(
                    provider="Google Vision",
                    success=False,
                    error="No se extrajo texto"
                )
                print(f"   ⚠️  Google Vision no extrajo texto")
                
        except Exception as e:
            result_obj = OCRTestResult(
                provider="Google Vision",
                success=True,  # Opcional
                error=f"Error: {str(e)} (opcional)"
            )
            print(f"   ⚠️  Error con Google Vision: {e} (opcional)")
        
        self.test_results.append(result_obj)
        return result_obj
    
    def test_aws_textract_ocr(self) -> OCRTestResult:
        """Testear AWS Textract OCR"""
        print("🔍 Testeando AWS Textract OCR...")
        
        start_time = time.time()
        
        try:
            ocr_service = OptimalOCRService()
            
            if not ocr_service.aws_textract:
                result_obj = OCRTestResult(
                    provider="AWS Textract",
                    success=True,  # Opcional, no es error
                    error="AWS Textract no configurado (opcional)"
                )
                print(f"   ⚠️  AWS Textract no configurado (opcional)")
                self.test_results.append(result_obj)
                return result_obj
            
            # Realizar OCR
            result = ocr_service.extract_text_from_image(self.test_image, provider="aws_textract")
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result and result.text:
                text_extracted = len(result.text.strip()) > 0
                confidence = result.confidence if hasattr(result, 'confidence') else None
                
                result_obj = OCRTestResult(
                    provider="AWS Textract",
                    success=True,
                    text_extracted=text_extracted,
                    confidence=confidence,
                    response_time_ms=elapsed_ms,
                    details={
                        "text_length": len(result.text),
                        "text_preview": result.text[:100] if result.text else ""
                    }
                )
                
                print(f"   ✅ AWS Textract funcionando ({elapsed_ms:.0f}ms)")
                print(f"      Texto extraído: {len(result.text)} caracteres")
                if confidence:
                    print(f"      Confianza: {confidence:.2f}")
                
            else:
                result_obj = OCRTestResult(
                    provider="AWS Textract",
                    success=False,
                    error="No se extrajo texto"
                )
                print(f"   ⚠️  AWS Textract no extrajo texto")
                
        except Exception as e:
            result_obj = OCRTestResult(
                provider="AWS Textract",
                success=True,  # Opcional
                error=f"Error: {str(e)} (opcional)"
            )
            print(f"   ⚠️  Error con AWS Textract: {e} (opcional)")
        
        self.test_results.append(result_obj)
        return result_obj
    
    def test_optimal_selection(self) -> OCRTestResult:
        """Testear selección automática de OCR"""
        print("🔍 Testeando selección automática de OCR...")
        
        start_time = time.time()
        
        try:
            ocr_service = OptimalOCRService()
            
            # Realizar OCR con selección automática
            result = ocr_service.extract_text_from_image(self.test_image)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result and result.text:
                provider_used = result.provider if hasattr(result, 'provider') else "unknown"
                
                result_obj = OCRTestResult(
                    provider="Optimal Selection",
                    success=True,
                    text_extracted=len(result.text.strip()) > 0,
                    response_time_ms=elapsed_ms,
                    details={
                        "provider_used": provider_used,
                        "text_length": len(result.text),
                        "text_preview": result.text[:100] if result.text else ""
                    }
                )
                
                print(f"   ✅ Selección automática funcionando ({elapsed_ms:.0f}ms)")
                print(f"      Proveedor usado: {provider_used}")
                print(f"      Texto extraído: {len(result.text)} caracteres")
                
            else:
                result_obj = OCRTestResult(
                    provider="Optimal Selection",
                    success=False,
                    error="No se extrajo texto"
                )
                print(f"   ❌ Selección automática no extrajo texto")
                
        except Exception as e:
            result_obj = OCRTestResult(
                provider="Optimal Selection",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error con selección automática: {e}")
        
        self.test_results.append(result_obj)
        return result_obj
    
    def test_fallback_mechanism(self) -> OCRTestResult:
        """Testear mecanismo de fallback"""
        print("🔍 Testeando mecanismo de fallback...")
        
        start_time = time.time()
        
        try:
            ocr_service = OptimalOCRService()
            
            # Intentar con un proveedor que puede no estar disponible
            # El servicio debería hacer fallback a Tesseract
            result = ocr_service.extract_text_from_image(
                self.test_image,
                provider="google_vision"  # Puede no estar configurado
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result and result.text:
                provider_used = result.provider if hasattr(result, 'provider') else "unknown"
                
                result_obj = OCRTestResult(
                    provider="Fallback Mechanism",
                    success=True,
                    text_extracted=len(result.text.strip()) > 0,
                    response_time_ms=elapsed_ms,
                    details={
                        "provider_used": provider_used,
                        "fallback_worked": provider_used == "tesseract" or provider_used == "google_vision"
                    }
                )
                
                print(f"   ✅ Fallback funcionando ({elapsed_ms:.0f}ms)")
                print(f"      Proveedor usado: {provider_used}")
                
            else:
                result_obj = OCRTestResult(
                    provider="Fallback Mechanism",
                    success=False,
                    error="No se extrajo texto incluso con fallback"
                )
                print(f"   ❌ Fallback no funcionó")
                
        except Exception as e:
            result_obj = OCRTestResult(
                provider="Fallback Mechanism",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error con fallback: {e}")
        
        self.test_results.append(result_obj)
        return result_obj
    
    def run_all_tests(self):
        """Ejecutar todos los tests OCR"""
        print("🚀 Iniciando tests de servicios OCR...")
        print("=" * 60)
        print()
        
        self.test_tesseract_ocr()
        self.test_google_vision_ocr()
        self.test_aws_textract_ocr()
        self.test_optimal_selection()
        self.test_fallback_mechanism()
        
        print()
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("=" * 60)
        print("📊 RESUMEN DE TESTS OCR")
        print("=" * 60)
        
        # Filtrar resultados opcionales (Google Vision, AWS Textract)
        required_results = [r for r in self.test_results if r.provider in ["Tesseract", "Optimal Selection", "Fallback Mechanism"]]
        optional_results = [r for r in self.test_results if r.provider in ["Google Vision", "AWS Textract"]]
        
        total_required = len(required_results)
        passed_required = sum(1 for r in required_results if r.success)
        
        total_optional = len(optional_results)
        passed_optional = sum(1 for r in optional_results if r.success)
        
        print(f"Tests requeridos: {passed_required}/{total_required}")
        print(f"Tests opcionales: {passed_optional}/{total_optional}")
        print()
        
        if passed_required < total_required:
            print("❌ Tests requeridos que fallaron:")
            for result in required_results:
                if not result.success:
                    print(f"   - {result.provider}: {result.error}")
            print()
        
        # Estadísticas de tiempo
        successful_results = [r for r in self.test_results if r.success and r.response_time_ms]
        if successful_results:
            avg_time = sum(r.response_time_ms for r in successful_results) / len(successful_results)
            print(f"⏱️  Tiempo promedio de OCR: {avg_time:.0f}ms")
            print()
        
        return passed_required == total_required


def main():
    """Función principal"""
    tester = OCRServiceTester()
    tester.run_all_tests()
    all_passed = tester.print_summary()
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())









































