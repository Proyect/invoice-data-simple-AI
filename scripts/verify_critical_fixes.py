#!/usr/bin/env python3
"""
Script de verificación de correcciones críticas
"""
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Verificar que requests está en requirements.txt"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("[FAIL] requirements.txt no encontrado")
        return False
    
    content = requirements_file.read_text()
    if "requests" not in content:
        print("[FAIL] requests no esta en requirements.txt")
        return False
    
    print("[OK] requests esta en requirements.txt")
    return True

def check_cache_consolidation():
    """Verificar que cache está consolidado"""
    cache_file = Path("src/app/services/cache.py")
    if not cache_file.exists():
        print("[FAIL] src/app/services/cache.py no existe")
        return False
    
    # Verificar que no hay imports a cache_service o cache_optimized
    try:
        result = subprocess.run(
            ["grep", "-r", "from.*cache_service import|from.*cache_optimized import", "src/app/"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Filtrar el archivo cache.py mismo
            lines = [l for l in result.stdout.split('\n') if l and 'cache.py' not in l]
            if lines:
                print("[WARN] Aun hay imports a cache_service o cache_optimized:")
                for line in lines[:5]:  # Mostrar solo los primeros 5
                    print(f"   {line}")
                return False
    except Exception as e:
        print(f"[WARN] Error verificando imports: {e}")
    
    # Verificar que los archivos legacy no existen
    if Path("src/app/services/cache_service.py").exists():
        print("[WARN] src/app/services/cache_service.py aun existe (deberia eliminarse)")
        return False
    
    if Path("src/app/services/cache_optimized.py").exists():
        print("[WARN] src/app/services/cache_optimized.py aun existe (deberia eliminarse)")
        return False
    
    print("[OK] Cache consolidado correctamente")
    return True

def check_config_migration():
    """Verificar migración de configuración"""
    config_file = Path("src/app/core/config.py")
    if not config_file.exists():
        print("[FAIL] src/app/core/config.py no existe")
        return False
    
    content = config_file.read_text()
    if "DEPRECATED" not in content:
        print("[WARN] config.py no tiene advertencia de deprecacion")
        return False
    
    # Verificar que no hay muchos archivos usando config.py directamente
    try:
        result = subprocess.run(
            ["grep", "-r", "from.*config import settings", "src/app/"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Contar líneas (excluyendo config.py mismo y dependencies.py que puede usarlo)
        lines = [l for l in result.stdout.split('\n') 
                if l and 'config.py' not in l and 'dependencies.py' not in l]
        
        if len(lines) > 3:  # Permitir algunos archivos legacy
            print(f"[WARN] Aun hay {len(lines)} archivos usando config.py directamente")
            for line in lines[:5]:
                print(f"   {line}")
            return False
    except Exception as e:
        print(f"[WARN] Error verificando imports: {e}")
    
    print("[OK] Configuracion migrada correctamente")
    return True

def check_imports_work():
    """Verificar que los imports funcionan"""
    try:
        # Intentar importar módulos clave
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from src.app.services.cache import get_cache_service
        from src.app.core.environment import get_settings
        from src.app.core.config import settings as config_settings
        
        # Verificar que funcionan
        cache = get_cache_service()
        settings = get_settings()
        
        assert cache is not None
        assert settings is not None
        assert config_settings is not None
        
        print("[OK] Todos los imports funcionan correctamente")
        return True
    except Exception as e:
        print(f"[FAIL] Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("Verificando correcciones criticas...\n")
    
    checks = [
        ("Requirements", check_requirements),
        ("Cache Consolidation", check_cache_consolidation),
        ("Config Migration", check_config_migration),
        ("Imports", check_imports_work),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nVerificando {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "="*50)
    print("Resumen de Verificacion")
    print("="*50)
    
    all_passed = True
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\nTodas las verificaciones pasaron!")
        return 0
    else:
        print("\nAlgunas verificaciones fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())

