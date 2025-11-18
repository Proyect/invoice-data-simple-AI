"""
Validacion Final del Sistema Completo
====================================

Script de validacion final para verificar que todo el sistema
esta funcionando correctamente en modo produccion.

Uso: python validacion_sistema_final.py
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

def print_header(title):
    """Imprimir encabezado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprimir mensaje de exito"""
    print(f"OK - {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"ERROR - {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"INFO - {message}")

def verificar_archivos_sistema():
    """Verificar que todos los archivos del sistema existen"""
    print_header("VERIFICACION DE ARCHIVOS DEL SISTEMA")
    
    archivos_requeridos = [
        "src/app/main.py",
        "src/app/core/config.py",
        "src/app/core/database.py",
        "src/app/models/document.py",
        "src/app/models/user.py",
        "src/app/schemas/document_enhanced.py",
        "src/app/schemas/user_enhanced_simple.py",
        "src/app/auth/dependencies.py",
        "src/app/auth/jwt_handler.py",
        "src/app/auth/password_handler.py",
        "start_production.py",
        "test_production_system.py",
        "requirements.txt",
        "README_PRODUCTION.md"
    ]
    
    archivos_ok = 0
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print_success(f"Archivo encontrado: {archivo}")
            archivos_ok += 1
        else:
            print_error(f"Archivo faltante: {archivo}")
            archivos_faltantes.append(archivo)
    
    print_info(f"Archivos verificados: {archivos_ok}/{len(archivos_requeridos)}")
    
    if archivos_faltantes:
        print_error(f"Archivos faltantes: {len(archivos_faltantes)}")
        return False
    
    return True

def verificar_directorios():
    """Verificar directorios necesarios"""
    print_header("VERIFICACION DE DIRECTORIOS")
    
    directorios = ["uploads", "outputs", "data", "logs"]
    
    for directorio in directorios:
        if os.path.exists(directorio):
            print_success(f"Directorio existe: {directorio}")
        else:
            print_info(f"Creando directorio: {directorio}")
            os.makedirs(directorio, exist_ok=True)
            print_success(f"Directorio creado: {directorio}")
    
    return True

def verificar_base_datos():
    """Verificar base de datos"""
    print_header("VERIFICACION DE BASE DE DATOS")
    
    try:
        # Configurar SQLite
        os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"
        
        # Agregar src al path
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        # Importar modelos
        from app.core.database import engine, Base
        from app.models.document import Document
        from app.models.user import User
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        print_success("Base de datos SQLite configurada correctamente")
        print_success("Tablas creadas exitosamente")
        
        return True
        
    except Exception as e:
        print_error(f"Error configurando base de datos: {e}")
        return False

def verificar_servidor():
    """Verificar que el servidor este funcionando"""
    print_header("VERIFICACION DEL SERVIDOR")
    
    base_url = "http://localhost:8000"
    
    try:
        # Probar health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print_success("Servidor respondiendo correctamente")
            
            health_data = response.json()
            print_info(f"Estado: {health_data.get('status', 'unknown')}")
            print_info(f"Version: {health_data.get('version', 'unknown')}")
            print_info(f"Base de datos: {health_data.get('database', 'unknown')}")
            
            return True
        else:
            print_error(f"Servidor respondiendo con codigo: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException:
        print_error("No se puede conectar al servidor")
        print_info("Asegurese de que el servidor este ejecutandose")
        print_info("Ejecute: python start_production.py")
        return False

def probar_endpoints_basicos():
    """Probar endpoints basicos del sistema"""
    print_header("PRUEBA DE ENDPOINTS BASICOS")
    
    base_url = "http://localhost:8000"
    endpoints = [
        ("/", "GET", 200, "Endpoint raiz"),
        ("/health", "GET", 200, "Health check"),
        ("/info", "GET", 200, "Informacion del sistema"),
        ("/docs", "GET", 200, "Documentacion Swagger")
    ]
    
    endpoints_ok = 0
    
    for endpoint, method, expected_status, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == expected_status:
                print_success(f"{description}: {method} {endpoint}")
                endpoints_ok += 1
            else:
                print_error(f"{description}: Esperado {expected_status}, obtenido {response.status_code}")
        except Exception as e:
            print_error(f"{description}: Error - {e}")
    
    print_info(f"Endpoints funcionando: {endpoints_ok}/{len(endpoints)}")
    return endpoints_ok == len(endpoints)

def probar_autenticacion():
    """Probar sistema de autenticacion"""
    print_header("PRUEBA DE AUTENTICACION")
    
    base_url = "http://localhost:8000"
    
    # Datos de prueba
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Usuario de Prueba",
        "password": "testpassword123"
    }
    
    login_data = {
        "username_or_email": "testuser",
        "password": "testpassword123"
    }
    
    try:
        # Registrar usuario
        response = requests.post(f"{base_url}/auth/register", json=user_data)
        if response.status_code == 200:
            print_success("Registro de usuario exitoso")
        else:
            print_info(f"Usuario ya existe o error: {response.status_code}")
        
        # Login
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            print_success("Login de usuario exitoso")
            
            # Obtener token
            token_data = response.json()
            token = token_data.get("access_token")
            
            if token:
                print_success("Token JWT obtenido correctamente")
                
                # Probar endpoint autenticado
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{base_url}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    print_success("Endpoint autenticado funcionando")
                    return True
                else:
                    print_error(f"Endpoint autenticado fallo: {response.status_code}")
                    return False
            else:
                print_error("No se pudo obtener token JWT")
                return False
        else:
            print_error(f"Login fallo: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en autenticacion: {e}")
        return False

def probar_documentos():
    """Probar operaciones de documentos"""
    print_header("PRUEBA DE OPERACIONES DE DOCUMENTOS")
    
    base_url = "http://localhost:8000"
    
    # Obtener token primero
    login_data = {
        "username_or_email": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code != 200:
            print_error("No se pudo autenticar para probar documentos")
            return False
        
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Listar documentos
        response = requests.get(f"{base_url}/api/v2/documents/", headers=headers)
        if response.status_code == 200:
            print_success("Listado de documentos funcionando")
        else:
            print_error(f"Listado de documentos fallo: {response.status_code}")
            return False
        
        # Obtener estadisticas
        response = requests.get(f"{base_url}/api/v2/documents/stats/overview", headers=headers)
        if response.status_code == 200:
            print_success("Estadisticas de documentos funcionando")
            
            stats = response.json()
            print_info(f"Total documentos: {stats.get('total_documents', 0)}")
            print_info(f"Documentos procesados: {stats.get('processed_documents', 0)}")
            print_info(f"Usuarios totales: {stats.get('total_users', 0)}")
        else:
            print_error(f"Estadisticas fallaron: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error probando documentos: {e}")
        return False

def generar_reporte_final(resultados):
    """Generar reporte final de validacion"""
    print_header("REPORTE FINAL DE VALIDACION")
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(1 for resultado in resultados.values() if resultado)
    porcentaje_exito = (pruebas_exitosas / total_pruebas * 100) if total_pruebas > 0 else 0
    
    print(f"RESUMEN DE VALIDACION:")
    print(f"  Total de pruebas: {total_pruebas}")
    print(f"  Exitosas: {pruebas_exitosas}")
    print(f"  Fallidas: {total_pruebas - pruebas_exitosas}")
    print(f"  Porcentaje de exito: {porcentaje_exito:.1f}%")
    
    print(f"\nDETALLE DE PRUEBAS:")
    for prueba, resultado in resultados.items():
        estado = "OK" if resultado else "ERROR"
        print(f"  {estado} - {prueba}")
    
    if porcentaje_exito >= 90:
        print(f"\nSISTEMA COMPLETAMENTE FUNCIONAL ({porcentaje_exito:.1f}% exito)")
        print("El sistema esta listo para produccion")
        return True
    elif porcentaje_exito >= 70:
        print(f"\nSISTEMA FUNCIONAL CON ALGUNOS PROBLEMAS ({porcentaje_exito:.1f}% exito)")
        print("Revise los errores antes de usar en produccion")
        return False
    else:
        print(f"\nSISTEMA CON PROBLEMAS CRITICOS ({porcentaje_exito:.1f}% exito)")
        print("Corrija los errores antes de continuar")
        return False

def main():
    """Funcion principal de validacion"""
    print("""
    ================================================================================
                    VALIDACION FINAL DEL SISTEMA DE PRODUCCION
    ================================================================================
    
    Este script valida que todos los componentes del sistema esten
    funcionando correctamente antes de considerar el sistema listo
    para produccion.
    
    ================================================================================
    """)
    
    print_info(f"Iniciando validacion: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las validaciones
    resultados = {
        "Archivos del sistema": verificar_archivos_sistema(),
        "Directorios necesarios": verificar_directorios(),
        "Base de datos": verificar_base_datos(),
        "Servidor funcionando": verificar_servidor(),
        "Endpoints basicos": probar_endpoints_basicos(),
        "Sistema de autenticacion": probar_autenticacion(),
        "Operaciones de documentos": probar_documentos()
    }
    
    # Generar reporte final
    exito = generar_reporte_final(resultados)
    
    print_info(f"Validacion completada: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if exito:
        print("\nFELICITACIONES! El sistema esta completamente funcional y listo para produccion.")
        print("Puede proceder con confianza a usar el sistema en produccion.")
    else:
        print("\nATENCION: El sistema tiene problemas que deben ser corregidos.")
        print("Revise los errores antes de usar el sistema en produccion.")
    
    return exito

if __name__ == "__main__":
    main()














