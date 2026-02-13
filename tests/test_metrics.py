"""
Tests para Sistema de Métricas
===============================
"""
import pytest
import time
from src.app.middleware.metrics import MetricsCollector


class TestMetrics:
    """Tests para el sistema de métricas"""
    
    def test_metrics_collector_initialization(self):
        """Test que el collector se inicializa correctamente"""
        collector = MetricsCollector()
        stats = collector.get_stats()
        
        assert "uptime_seconds" in stats
        assert "total_requests" in stats
        assert "requests_per_second" in stats
        assert "endpoints" in stats
        assert "errors" in stats
        assert stats["total_requests"] == 0
    
    def test_metrics_collector_records_requests(self):
        """Test que el collector registra peticiones"""
        collector = MetricsCollector()
        collector.reset()
        
        # Simular peticiones
        collector.record_request("GET", "/test", 200, 0.1)
        collector.record_request("POST", "/test", 201, 0.2)
        
        stats = collector.get_stats()
        assert stats["total_requests"] == 2
        assert "GET /test" in stats["endpoints"]
        assert "POST /test" in stats["endpoints"]
    
    def test_metrics_collector_records_errors(self):
        """Test que el collector registra errores"""
        collector = MetricsCollector()
        collector.reset()
        
        # Simular errores
        collector.record_request("GET", "/test", 404, 0.1)
        collector.record_request("GET", "/test", 500, 0.1)
        
        stats = collector.get_stats()
        # Los errores se almacenan como enteros, no strings
        assert stats["errors"][404] == 1
        assert stats["errors"][500] == 1
    
    def test_metrics_collector_reset(self):
        """Test que el reset funciona correctamente"""
        collector = MetricsCollector()
        
        # Registrar algunas peticiones
        collector.record_request("GET", "/test", 200, 0.1)
        
        stats_before = collector.get_stats()
        assert stats_before["total_requests"] > 0
        
        # Resetear
        collector.reset()
        
        stats_after = collector.get_stats()
        assert stats_after["total_requests"] == 0
        assert stats_after["uptime_seconds"] >= 0
    
    def test_metrics_collector_uptime(self):
        """Test que el uptime se calcula correctamente"""
        collector = MetricsCollector()
        collector.reset()
        
        time.sleep(0.1)  # Esperar un poco
        
        stats = collector.get_stats()
        assert stats["uptime_seconds"] >= 0.1

