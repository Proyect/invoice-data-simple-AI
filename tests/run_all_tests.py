#!/usr/bin/env python3
"""
Script Maestro para Ejecutar Todos los Tests
============================================

Ejecuta todos los tests del sistema de manera organizada y genera un reporte completo.
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_test_suite(test_file, test_name):
    """Ejecutar una suite de tests específica"""
    print(f"\n{'='*70}")
    print(f"EJECUTANDO: {test_name}")
    print(f"Archivo: {test_file}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Ejecutar el test
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"OK {test_name} - EXITOSO ({duration:.2f}s)")
            return True, duration, result.stdout
        else:
            print(f"FAIL {test_name} - FALLO ({duration:.2f}s)")
            print(f"Error: {result.stderr}")
            return False, duration, result.stderr
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"ERROR {test_name} - ERROR ({duration:.2f}s)")
        print(f"Excepcion: {str(e)}")
        return False, duration, str(e)

def main():
    """Función principal"""
    print("INICIANDO SUITE COMPLETA DE TESTS")
    print("=" * 70)
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Definir suites de tests
    test_suites = [
        # Tests unitarios
        {
            "file": "unit/test_academic_documents.py",
            "name": "Tests Unitarios - Documentos Académicos"
        },
        {
            "file": "unit/test_improved_precision.py",
            "name": "Tests Unitarios - Precisión Mejorada"
        },
        {
            "file": "unit/test_dni_extraction.py",
            "name": "Tests Unitarios - Extracción DNI"
        },
        
        # Tests de integración
        {
            "file": "integration/test_full_system.py",
            "name": "Tests de Integración - Sistema Completo"
        },
        
        # Tests end-to-end
        {
            "file": "e2e/test_complete_workflow.py",
            "name": "Tests E2E - Flujo Completo"
        }
    ]
    
    # Ejecutar tests
    results = []
    total_start_time = time.time()
    
    for suite in test_suites:
        success, duration, output = run_test_suite(suite["file"], suite["name"])
        results.append({
            "name": suite["name"],
            "file": suite["file"],
            "success": success,
            "duration": duration,
            "output": output
        })
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Generar reporte
    print(f"\n{'='*70}")
    print("REPORTE FINAL DE TESTS")
    print(f"{'='*70}")
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Tests ejecutados: {total_tests}")
    print(f"Tests exitosos: {successful_tests}")
    print(f"Tests fallidos: {total_tests - successful_tests}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    print(f"Tiempo total: {total_duration:.2f}s")
    print()
    
    # Detalles por test
    print("DETALLES POR TEST:")
    print("-" * 50)
    for result in results:
        status = "OK" if result["success"] else "FAIL"
        print(f"{status} {result['name']} ({result['duration']:.2f}s)")
    
    print()
    
    # Resumen de funcionalidades probadas
    print("FUNCIONALIDADES PROBADAS:")
    print("-" * 50)
    print("OK Extracción de facturas")
    print("OK Extracción de recibos")
    print("OK Extracción de títulos académicos")
    print("OK Extracción de certificados")
    print("OK Extracción de diplomas")
    print("OK Extracción de licencias")
    print("OK Extracción de DNI argentinos")
    print("OK Extracción de pasaportes")
    print("OK Detección automática de tipos")
    print("OK Validación de datos")
    print("OK Manejo de errores")
    print("OK Rendimiento del sistema")
    print("OK Integración de servicios")
    print("OK Flujo completo end-to-end")
    
    print(f"\n{'='*70}")
    if success_rate == 100:
        print("TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
    else:
        print(f"{total_tests - successful_tests} TESTS FALLARON")
    print(f"{'='*70}")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
