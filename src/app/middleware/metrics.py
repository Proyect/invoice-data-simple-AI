"""
Metrics Middleware
==================

Middleware básico para recopilar métricas de la aplicación.
"""
import time
import logging
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Recopilador básico de métricas en memoria"""
    
    def __init__(self):
        self.request_count = 0
        self.request_times: Dict[str, list] = defaultdict(list)
        self.error_count = defaultdict(int)
        self.endpoint_count = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Registrar una petición"""
        self.request_count += 1
        endpoint = f"{method} {path}"
        self.endpoint_count[endpoint] += 1
        self.request_times[endpoint].append(duration)
        
        # Mantener solo últimos 1000 tiempos por endpoint
        if len(self.request_times[endpoint]) > 1000:
            self.request_times[endpoint] = self.request_times[endpoint][-1000:]
        
        if status_code >= 400:
            self.error_count[status_code] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas agregadas"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calcular tiempos promedio por endpoint
        avg_times = {}
        for endpoint, times in self.request_times.items():
            if times:
                avg_times[endpoint] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
            "endpoints": {
                endpoint: {
                    "count": count,
                    "avg_time_ms": sum(self.request_times[endpoint]) / len(self.request_times[endpoint]) * 1000 if self.request_times[endpoint] else 0
                }
                for endpoint, count in self.endpoint_count.items()
            },
            "errors": dict(self.error_count),
            "average_response_times": avg_times
        }
    
    def reset(self):
        """Resetear métricas (útil para testing)"""
        self.request_count = 0
        self.request_times.clear()
        self.error_count.clear()
        self.endpoint_count.clear()
        self.start_time = datetime.now()


# Instancia global del recopilador
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para recopilar métricas de peticiones HTTP"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Procesar petición y recopilar métricas"""
        start_time = time.time()
        
        # Excluir endpoints de métricas y health checks
        if request.url.path in ["/metrics", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration=duration
            )
        
        return response


def get_metrics() -> Dict[str, Any]:
    """Obtener métricas actuales"""
    return metrics_collector.get_stats()





































