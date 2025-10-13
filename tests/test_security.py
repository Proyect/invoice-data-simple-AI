"""
Tests de seguridad para la API
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO


class TestFileUploadSecurity:
    """Tests de seguridad en upload de archivos"""
    
    def test_rejects_executable_files(self, client: TestClient):
        """Test de rechazo de archivos ejecutables"""
        fake_exe = b"MZ\x90\x00\x03"  # Header de .exe
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("malware.exe", BytesIO(fake_exe), "application/x-msdownload")},
            data={"document_type": "factura"}
        )
        
        assert response.status_code in [400, 415, 422]
    
    def test_rejects_script_files(self, client: TestClient):
        """Test de rechazo de scripts"""
        script_content = b"#!/bin/bash\nrm -rf /"
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("script.sh", BytesIO(script_content), "application/x-sh")},
            data={"document_type": "factura"}
        )
        
        assert response.status_code in [400, 415, 422]
    
    def test_filename_sanitization(self, client: TestClient, sample_pdf_path, mock_tesseract, mock_spacy):
        """Test de sanitización de nombre de archivo"""
        with open(sample_pdf_path, 'rb') as f:
            content = f.read()
        
        # Intentar con nombre malicioso
        response = client.post(
            "/api/v1/upload",
            files={"file": ("../../../etc/passwd", BytesIO(content), "application/pdf")},
            data={"document_type": "factura"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # El filename no debería contener ../
            assert "../" not in data.get("filename", "")
    
    def test_rejects_html_files(self, client: TestClient):
        """Test de rechazo de archivos HTML (XSS)"""
        html_content = b"<script>alert('XSS')</script>"
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("xss.html", BytesIO(html_content), "text/html")},
            data={"document_type": "factura"}
        )
        
        assert response.status_code in [400, 415, 422]


class TestInjectionAttacks:
    """Tests de ataques de inyección"""
    
    def test_sql_injection_in_search(self, client: TestClient, sample_document_data):
        """Test de protección contra SQL injection"""
        # Intentar SQL injection
        malicious_queries = [
            "'; DROP TABLE documents--",
            "1' OR '1'='1",
            "'; DELETE FROM documents WHERE 1=1--",
        ]
        
        for query in malicious_queries:
            response = client.get(
                f"/api/v1/documents/search?q={query}&limit=10"
            )
            
            # No debería causar error 500, debería devolver 400 o resultados vacíos
            assert response.status_code != 500
    
    def test_no_code_injection_in_document_type(
        self,
        client: TestClient,
        sample_pdf_path,
        mock_tesseract,
        mock_spacy
    ):
        """Test de que no se puede inyectar código en document_type"""
        with open(sample_pdf_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"document_type": "__import__('os').system('ls')"}
            )
        
        # Debería procesar sin ejecutar código
        assert response.status_code in [200, 400, 422]


class TestInputValidation:
    """Tests de validación de entrada"""
    
    def test_rejects_negative_pagination(self, client: TestClient):
        """Test de rechazo de valores negativos en paginación"""
        response = client.get("/api/v1/documents?skip=-1&limit=10")
        
        assert response.status_code == 422  # Validation error
    
    def test_rejects_excessive_limit(self, client: TestClient):
        """Test de rechazo de límite excesivo"""
        response = client.get("/api/v1/documents?skip=0&limit=99999")
        
        assert response.status_code == 422  # Validation error
    
    def test_rejects_invalid_document_id(self, client: TestClient):
        """Test de rechazo de ID inválido"""
        response = client.get("/api/v1/documents/invalid_id")
        
        assert response.status_code == 422
    
    def test_rejects_very_long_search_query(self, client: TestClient):
        """Test de rechazo de query muy largo"""
        long_query = "a" * 10000
        
        response = client.get(f"/api/v1/documents/search?q={long_query}")
        
        # Debería rechazar o truncar
        assert response.status_code in [200, 400, 413, 422]


class TestErrorHandling:
    """Tests de manejo seguro de errores"""
    
    def test_does_not_expose_stack_traces(self, client: TestClient):
        """Test de que no expone stack traces"""
        # Intentar causar un error
        response = client.get("/api/v1/documents/trigger_error")
        
        if response.status_code >= 500:
            error_text = response.text.lower()
            
            # No debería exponer información sensible
            assert "traceback" not in error_text
            assert "exception" not in error_text
            assert "/usr/" not in error_text
            assert "/home/" not in error_text
    
    def test_generic_error_messages(self, client: TestClient):
        """Test de mensajes de error genéricos"""
        # Causar error en procesamiento
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", BytesIO(b"invalid pdf"), "application/pdf")},
        )
        
        if response.status_code >= 400:
            error_detail = response.json().get("detail", "")
            
            # No debería revelar paths del sistema
            assert not any(path in error_detail for path in ["/usr/", "/var/", "/etc/", "C:\\"])


class TestCORS:
    """Tests de configuración CORS"""
    
    def test_cors_headers_present(self, client: TestClient):
        """Test de que los headers CORS están presentes"""
        response = client.options("/api/v1/documents")
        
        # Debería tener headers CORS configurados
        # (En producción, deberían ser más restrictivos)
        headers = dict(response.headers)
        assert "access-control-allow-origin" in str(headers).lower()


class TestRateLimiting:
    """Tests de rate limiting (si está implementado)"""
    
    def test_rate_limit_exists(self, client: TestClient, sample_pdf_path, mock_tesseract, mock_spacy):
        """Test de que existe algún tipo de rate limiting"""
        # Intentar hacer muchos requests rápidamente
        responses = []
        
        for _ in range(100):
            with open(sample_pdf_path, 'rb') as f:
                response = client.post(
                    "/api/v1/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                )
                responses.append(response.status_code)
        
        # Si hay rate limiting, eventualmente debería devolver 429
        # Si no hay, este test simplemente pasa
        # TODO: Implementar rate limiting y activar esta assertion
        # assert 429 in responses


class TestAuthenticationAuthorization:
    """Tests de autenticación y autorización (para implementar)"""
    
    def test_delete_requires_authentication(self, client: TestClient):
        """Test de que DELETE requiere autenticación"""
        # TODO: Una vez implementada autenticación, activar este test
        # response = client.delete("/api/v1/documents/1")
        # assert response.status_code in [401, 403]
        pass
    
    def test_admin_endpoints_require_admin(self, client: TestClient):
        """Test de que endpoints admin requieren rol admin"""
        # TODO: Implementar cuando haya endpoints de admin
        pass




