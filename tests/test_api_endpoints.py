#!/usr/bin/env python3
"""
Test de Endpoints API
=====================

Tests completos de todos los endpoints API (v1 y v2).
"""
import sys
import os
import requests
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8006")


@dataclass
class EndpointTestResult:
    """Resultado de test de un endpoint"""
    method: str
    path: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    response_data: Optional[Dict] = None


class APIEndpointTester:
    """Tester para endpoints API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.test_results: List[EndpointTestResult] = []
    
    def test_endpoint(
        self,
        method: str,
        path: str,
        expected_status: int = 200,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30
    ) -> EndpointTestResult:
        """Testear un endpoint"""
        url = f"{self.base_url}{path}"
        
        # Agregar token de autenticación si está disponible
        request_headers = headers or {}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        result = EndpointTestResult(method=method, path=path)
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=timeout)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(
                        url,
                        files=files,
                        data=json_data,
                        headers=request_headers,
                        timeout=timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        json=json_data,
                        headers=request_headers,
                        timeout=timeout
                    )
            elif method.upper() == "PUT":
                response = self.session.put(
                    url,
                    json=json_data,
                    headers=request_headers,
                    timeout=timeout
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, timeout=timeout)
            else:
                result.error = f"Método HTTP no soportado: {method}"
                self.test_results.append(result)
                return result
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result.status_code = response.status_code
            result.response_time_ms = elapsed_ms
            result.success = response.status_code == expected_status
            
            try:
                result.response_data = response.json()
            except:
                result.response_data = {"raw": response.text[:200]}
            
            if not result.success:
                result.error = f"Status code esperado {expected_status}, obtenido {response.status_code}"
            
        except requests.exceptions.Timeout:
            result.error = "Timeout"
        except requests.exceptions.ConnectionError:
            result.error = "Error de conexión - ¿Está el servidor corriendo?"
        except Exception as e:
            result.error = f"Error: {str(e)}"
        
        self.test_results.append(result)
        return result
    
    def test_system_endpoints(self):
        """Testear endpoints del sistema"""
        print("🔍 Testeando endpoints del sistema...")
        print("-" * 60)
        
        # GET /
        result = self.test_endpoint("GET", "/", expected_status=200)
        self._print_result("GET /", result)
        
        # GET /health
        result = self.test_endpoint("GET", "/health", expected_status=200)
        self._print_result("GET /health", result)
        
        # GET /info
        result = self.test_endpoint("GET", "/info", expected_status=200)
        self._print_result("GET /info", result)
        
        # GET /docs (Swagger)
        result = self.test_endpoint("GET", "/docs", expected_status=200)
        self._print_result("GET /docs", result)
        
        print()
    
    def test_auth_endpoints(self):
        """Testear endpoints de autenticación"""
        print("🔐 Testeando endpoints de autenticación...")
        print("-" * 60)
        
        # POST /auth/register
        register_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!"
        }
        result = self.test_endpoint("POST", "/auth/register", json_data=register_data, expected_status=201)
        self._print_result("POST /auth/register", result)
        
        # POST /auth/login
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        result = self.test_endpoint("POST", "/auth/login", json_data=login_data, expected_status=200)
        self._print_result("POST /auth/login", result)
        
        # Guardar token si el login fue exitoso
        if result.success and result.response_data:
            access_token = result.response_data.get("access_token")
            if access_token:
                self.auth_token = access_token
                print(f"   ✅ Token de autenticación obtenido")
        
        print()
    
    def test_api_v1_documents(self):
        """Testear endpoints de documentos API v1"""
        print("📄 Testeando endpoints de documentos API v1...")
        print("-" * 60)
        
        # GET /api/v1/documents
        result = self.test_endpoint("GET", "/api/v1/documents", expected_status=200)
        self._print_result("GET /api/v1/documents", result)
        
        # GET /api/v1/documents con parámetros
        result = self.test_endpoint(
            "GET",
            "/api/v1/documents?skip=0&limit=5",
            expected_status=200
        )
        self._print_result("GET /api/v1/documents (con parámetros)", result)
        
        # Obtener ID de documento si hay documentos
        document_id = None
        if result.success and result.response_data:
            documents = result.response_data.get("documents", [])
            if documents:
                document_id = documents[0].get("id")
        
        # GET /api/v1/documents/{id}
        if document_id:
            result = self.test_endpoint(
                "GET",
                f"/api/v1/documents/{document_id}",
                expected_status=200
            )
            self._print_result(f"GET /api/v1/documents/{document_id}", result)
        else:
            print("   ⚠️  No hay documentos para probar GET por ID")
        
        print()
    
    def test_api_v1_uploads(self):
        """Testear endpoints de upload API v1"""
        print("📤 Testeando endpoints de upload API v1...")
        print("-" * 60)
        
        # Crear un archivo de prueba simple
        test_file_content = b"Test PDF content"
        test_file = ("test.pdf", test_file_content, "application/pdf")
        
        files = {"file": test_file}
        data = {"document_type": "factura"}
        
        # POST /api/v1/upload
        result = self.test_endpoint(
            "POST",
            "/api/v1/upload",
            files=files,
            json_data=data,
            expected_status=200,
            timeout=60
        )
        self._print_result("POST /api/v1/upload", result)
        
        print()
    
    def test_api_v2_documents(self):
        """Testear endpoints de documentos API v2"""
        print("📄 Testeando endpoints de documentos API v2...")
        print("-" * 60)
        
        # GET /api/v2/documents/
        result = self.test_endpoint("GET", "/api/v2/documents/", expected_status=200)
        self._print_result("GET /api/v2/documents/", result)
        
        # GET /api/v2/documents/ con filtros
        result = self.test_endpoint(
            "GET",
            "/api/v2/documents/?skip=0&limit=10&status=processed",
            expected_status=200
        )
        self._print_result("GET /api/v2/documents/ (con filtros)", result)
        
        # Obtener ID de documento si hay documentos
        document_id = None
        if result.success and result.response_data:
            documents = result.response_data.get("documents", [])
            if documents:
                document_id = documents[0].get("id")
        
        # GET /api/v2/documents/{id}
        if document_id:
            result = self.test_endpoint(
                "GET",
                f"/api/v2/documents/{document_id}",
                expected_status=200
            )
            self._print_result(f"GET /api/v2/documents/{document_id}", result)
        else:
            print("   ⚠️  No hay documentos para probar GET por ID")
        
        # POST /api/v2/documents/search
        search_data = {
            "query": "test",
            "limit": 10
        }
        result = self.test_endpoint(
            "POST",
            "/api/v2/documents/search",
            json_data=search_data,
            expected_status=200
        )
        self._print_result("POST /api/v2/documents/search", result)
        
        print()
    
    def test_api_v2_uploads(self):
        """Testear endpoints de upload API v2"""
        print("📤 Testeando endpoints de upload API v2...")
        print("-" * 60)
        
        # Crear un archivo de prueba simple
        test_file_content = b"Test PDF content for v2"
        test_file = ("test_v2.pdf", test_file_content, "application/pdf")
        
        files = {"file": test_file}
        data = {"document_type": "factura"}
        
        # POST /api/v2/uploads/
        result = self.test_endpoint(
            "POST",
            "/api/v2/uploads/",
            files=files,
            json_data=data,
            expected_status=200,
            timeout=60
        )
        self._print_result("POST /api/v2/uploads/", result)
        
        print()
    
    def test_api_v2_processing(self):
        """Testear endpoints de procesamiento API v2"""
        print("⚙️  Testeando endpoints de procesamiento API v2...")
        print("-" * 60)
        
        # Obtener un documento ID primero
        list_result = self.test_endpoint("GET", "/api/v2/documents/?limit=1", expected_status=200)
        document_id = None
        
        if list_result.success and list_result.response_data:
            documents = list_result.response_data.get("documents", [])
            if documents:
                document_id = documents[0].get("id")
        
        if document_id:
            # POST /api/v2/documents/{id}/process
            process_data = {
                "force_reprocess": False
            }
            result = self.test_endpoint(
                "POST",
                f"/api/v2/documents/{document_id}/process",
                json_data=process_data,
                expected_status=200,
                timeout=60
            )
            self._print_result(f"POST /api/v2/documents/{document_id}/process", result)
        else:
            print("   ⚠️  No hay documentos para procesar")
        
        print()
    
    def _print_result(self, endpoint_name: str, result: EndpointTestResult):
        """Imprimir resultado de un test"""
        if result.success:
            status_icon = "✅"
            time_info = f" ({result.response_time_ms:.0f}ms)" if result.response_time_ms else ""
            print(f"   {status_icon} {endpoint_name}{time_info}")
        else:
            status_icon = "❌"
            error_info = f" - {result.error}" if result.error else ""
            status_info = f" (Status: {result.status_code})" if result.status_code else ""
            print(f"   {status_icon} {endpoint_name}{status_info}{error_info}")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 Iniciando tests de endpoints API...")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print()
        
        # Verificar que el servidor esté disponible
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"❌ El servidor no está respondiendo correctamente")
                print(f"   Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ No se puede conectar al servidor: {e}")
            print(f"   Verifica que el servidor esté corriendo en {self.base_url}")
            return False
        
        print("✅ Servidor accesible\n")
        
        # Ejecutar tests
        self.test_system_endpoints()
        self.test_auth_endpoints()
        self.test_api_v1_documents()
        self.test_api_v1_uploads()
        self.test_api_v2_documents()
        self.test_api_v2_uploads()
        self.test_api_v2_processing()
        
        return True
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("=" * 60)
        print("📊 RESUMEN DE TESTS DE ENDPOINTS")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.success)
        failed = total - passed
        
        print(f"Total de tests: {total}")
        print(f"Pasaron: {passed}")
        print(f"Fallaron: {failed}")
        print(f"Tasa de éxito: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print()
        
        if failed > 0:
            print("❌ Tests que fallaron:")
            for result in self.test_results:
                if not result.success:
                    print(f"   - {result.method} {result.path}: {result.error}")
            print()
        
        # Estadísticas de tiempo de respuesta
        successful_results = [r for r in self.test_results if r.success and r.response_time_ms]
        if successful_results:
            avg_time = sum(r.response_time_ms for r in successful_results) / len(successful_results)
            max_time = max(r.response_time_ms for r in successful_results)
            min_time = min(r.response_time_ms for r in successful_results)
            
            print("⏱️  Estadísticas de tiempo de respuesta:")
            print(f"   Promedio: {avg_time:.0f}ms")
            print(f"   Mínimo: {min_time:.0f}ms")
            print(f"   Máximo: {max_time:.0f}ms")
            print()
        
        return failed == 0


def main():
    """Función principal"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8006")
    tester = APIEndpointTester(base_url)
    
    success = tester.run_all_tests()
    if success:
        all_passed = tester.print_summary()
        return 0 if all_passed else 1
    else:
        return 1


if __name__ == "__main__":
    exit(main())






































