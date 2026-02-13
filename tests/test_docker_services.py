#!/usr/bin/env python3
"""
Test de Servicios Docker
=========================

Verifica el estado de todos los contenedores Docker y su conectividad.
"""
import subprocess
import socket
import requests
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServiceStatus:
    """Estado de un servicio"""
    name: str
    container_name: str
    running: bool
    port: Optional[int] = None
    accessible: bool = False
    health: Optional[str] = None
    error: Optional[str] = None


class DockerServiceTester:
    """Tester para servicios Docker"""
    
    def __init__(self):
        self.services = {
            "app": {
                "container": "invoice-data-simple-ai-app-1",
                "port": 8006,
                "health_endpoint": "http://localhost:8006/health"
            },
            "postgres": {
                "container": "invoice-data-simple-ai-postgres-1",
                "port": 5434,
                "health_endpoint": None
            },
            "redis": {
                "container": "invoice-data-simple-ai-redis-1",
                "port": 6380,
                "health_endpoint": None
            },
            "worker": {
                "container": "invoice-data-simple-ai-worker-1",
                "port": None,
                "health_endpoint": None
            },
            "frontend": {
                "container": "invoice-data-simple-ai-frontend-1",
                "port": 3001,
                "health_endpoint": "http://localhost:3001"
            }
        }
    
    def check_docker_available(self) -> bool:
        """Verificar si Docker está disponible"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_container_status(self, container_name: str) -> Tuple[bool, Optional[str]]:
        """Verificar estado de un contenedor"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Error ejecutando docker ps: {result.stderr}"
            
            status = result.stdout.strip()
            if not status:
                return False, "Contenedor no encontrado"
            
            # Verificar si está corriendo
            if "Up" in status:
                return True, status
            else:
                return False, status
                
        except subprocess.TimeoutExpired:
            return False, "Timeout al verificar contenedor"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_port_accessible(self, host: str, port: int, timeout: int = 5) -> bool:
        """Verificar si un puerto está accesible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def check_http_endpoint(self, url: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """Verificar endpoint HTTP"""
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return True, "OK"
            else:
                return False, f"Status code: {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_container_logs(self, container_name: str, lines: int = 50) -> Optional[str]:
        """Obtener logs de un contenedor"""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None
    
    def check_service(self, service_name: str, config: Dict) -> ServiceStatus:
        """Verificar un servicio completo"""
        container_name = config["container"]
        port = config.get("port")
        health_endpoint = config.get("health_endpoint")
        
        # Verificar contenedor
        running, status = self.check_container_status(container_name)
        
        service_status = ServiceStatus(
            name=service_name,
            container_name=container_name,
            running=running,
            port=port,
            health=status
        )
        
        if not running:
            service_status.error = f"Contenedor no está corriendo: {status}"
            return service_status
        
        # Verificar puerto si está configurado
        if port:
            service_status.accessible = self.check_port_accessible("localhost", port)
            if not service_status.accessible:
                service_status.error = f"Puerto {port} no accesible"
        
        # Verificar endpoint de health si está configurado
        if health_endpoint and service_status.accessible:
            accessible, message = self.check_http_endpoint(health_endpoint)
            if accessible:
                service_status.accessible = True
            else:
                service_status.error = f"Health endpoint no accesible: {message}"
        
        return service_status
    
    def test_all_services(self) -> Dict[str, ServiceStatus]:
        """Testear todos los servicios"""
        results = {}
        
        print("🔍 Verificando servicios Docker...")
        print("=" * 60)
        
        # Verificar Docker
        if not self.check_docker_available():
            print("❌ Docker no está disponible")
            return results
        
        print("✅ Docker está disponible\n")
        
        # Verificar cada servicio
        for service_name, config in self.services.items():
            print(f"📦 Verificando {service_name}...")
            status = self.check_service(service_name, config)
            results[service_name] = status
            
            if status.running and status.accessible:
                print(f"   ✅ {service_name} - CORRIENDO y ACCESIBLE")
                if status.health:
                    print(f"      Estado: {status.health}")
            elif status.running:
                print(f"   ⚠️  {service_name} - CORRIENDO pero NO ACCESIBLE")
                if status.error:
                    print(f"      Error: {status.error}")
            else:
                print(f"   ❌ {service_name} - NO CORRIENDO")
                if status.error:
                    print(f"      Error: {status.error}")
            
            print()
        
        return results
    
    def get_failed_services(self, results: Dict[str, ServiceStatus]) -> List[str]:
        """Obtener lista de servicios que fallaron"""
        failed = []
        for name, status in results.items():
            if not status.running or not status.accessible:
                failed.append(name)
        return failed
    
    def print_summary(self, results: Dict[str, ServiceStatus]):
        """Imprimir resumen de resultados"""
        print("=" * 60)
        print("📊 RESUMEN DE SERVICIOS DOCKER")
        print("=" * 60)
        
        total = len(results)
        running = sum(1 for s in results.values() if s.running)
        accessible = sum(1 for s in results.values() if s.running and s.accessible)
        
        print(f"Total de servicios: {total}")
        print(f"Corriendo: {running}/{total}")
        print(f"Accesibles: {accessible}/{total}")
        print()
        
        failed = self.get_failed_services(results)
        if failed:
            print(f"❌ Servicios con problemas: {', '.join(failed)}")
        else:
            print("✅ Todos los servicios están funcionando correctamente")
        
        print()


def main():
    """Función principal"""
    tester = DockerServiceTester()
    results = tester.test_all_services()
    tester.print_summary(results)
    
    # Retornar código de salida
    failed = tester.get_failed_services(results)
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())






































