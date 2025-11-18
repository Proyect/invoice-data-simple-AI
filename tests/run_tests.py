#!/usr/bin/env python3
"""
Script Principal de Tests
=========================

Script para ejecutar todos los tests del sistema de forma organizada.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_pytest_tests(test_paths: List[str], verbose: bool = False) -> Dict[str, Any]:
    """Ejecutar tests con pytest"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(test_paths)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": str(e)
        }


def run_individual_tests() -> Dict[str, Any]:
    """Ejecutar tests individuales"""
    results = {}
    
    # Test del sistema optimizado
    print("🔄 Ejecutando test del sistema optimizado...")
    try:
        from test_optimized_system import main as test_optimized_main
        results["optimized_system"] = {
            "success": test_optimized_main() == 0,
            "name": "Sistema Optimizado"
        }
    except Exception as e:
        results["optimized_system"] = {
            "success": False,
            "name": "Sistema Optimizado",
            "error": str(e)
        }
    
    # Test del sistema de producción
    print("🔄 Ejecutando test del sistema de producción...")
    try:
        from test_production_system import test_system
        results["production_system"] = {
            "success": test_system(),
            "name": "Sistema de Producción"
        }
    except Exception as e:
        results["production_system"] = {
            "success": False,
            "name": "Sistema de Producción",
            "error": str(e)
        }
    
    return results


def run_all_tests(test_type: str = "all", verbose: bool = False) -> Dict[str, Any]:
    """Ejecutar todos los tests"""
    print("🚀 Iniciando ejecución de tests...")
    print(f"📋 Tipo de tests: {test_type}")
    print(f"📊 Modo verbose: {verbose}")
    print("=" * 50)
    
    results = {
        "test_type": test_type,
        "verbose": verbose,
        "pytest_results": {},
        "individual_results": {},
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "success_rate": 0.0
        }
    }
    
    # Ejecutar tests con pytest si se solicita
    if test_type in ["all", "pytest", "unit"]:
        print("\n📋 Ejecutando tests unitarios con pytest...")
        
        pytest_paths = []
        
        if test_type == "unit":
            pytest_paths = [
                "test_models.py",
                "test_repositories.py", 
                "test_cache.py",
                "test_schemas.py"
            ]
        else:
            pytest_paths = ["."]
        
        pytest_results = run_pytest_tests(pytest_paths, verbose)
        results["pytest_results"] = pytest_results
        
        if pytest_results["success"]:
            print("✅ Tests de pytest completados exitosamente")
        else:
            print("❌ Tests de pytest fallaron")
            if verbose:
                print("STDOUT:", pytest_results["stdout"])
                print("STDERR:", pytest_results["stderr"])
    
    # Ejecutar tests individuales si se solicita
    if test_type in ["all", "individual", "integration"]:
        print("\n📋 Ejecutando tests individuales...")
        
        individual_results = run_individual_tests()
        results["individual_results"] = individual_results
        
        for test_name, test_result in individual_results.items():
            if test_result["success"]:
                print(f"✅ {test_result['name']} - PASÓ")
            else:
                print(f"❌ {test_result['name']} - FALLÓ")
                if "error" in test_result:
                    print(f"   Error: {test_result['error']}")
    
    # Calcular resumen
    total_tests = 0
    passed_tests = 0
    
    # Contar tests de pytest
    if "pytest_results" in results and results["pytest_results"]:
        total_tests += 1
        if results["pytest_results"]["success"]:
            passed_tests += 1
    
    # Contar tests individuales
    if "individual_results" in results and results["individual_results"]:
        for test_result in results["individual_results"].values():
            total_tests += 1
            if test_result["success"]:
                passed_tests += 1
    
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": success_rate
    }
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    print(f"Total de tests: {total_tests}")
    print(f"Pasaron: {passed_tests}")
    print(f"Fallaron: {failed_tests}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ¡Todos los tests pasaron!")
    elif success_rate >= 80:
        print(f"\n✅ Tests completados con {success_rate:.1f}% de éxito")
    else:
        print(f"\n⚠️ Tests completados con {success_rate:.1f}% de éxito - Revisar fallos")
    
    return results


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Ejecutar tests del sistema")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "individual", "integration", "pytest"],
        default="all",
        help="Tipo de tests a ejecutar"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verbose"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Ejecutar con cobertura de código"
    )
    
    args = parser.parse_args()
    
    # Configurar cobertura si se solicita
    if args.coverage:
        os.environ["COVERAGE"] = "true"
    
    # Ejecutar tests
    results = run_all_tests(args.type, args.verbose)
    
    # Retornar código de salida apropiado
    if results["summary"]["success_rate"] == 100:
        return 0
    elif results["summary"]["success_rate"] >= 80:
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit(main())





