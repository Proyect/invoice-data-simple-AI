#!/usr/bin/env python3
"""
Script para corregir importaciones de 'app.' a importaciones relativas
"""
import os
import re

def fix_imports_in_file(file_path):
    """Corregir importaciones en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar importaciones absolutas con relativas
        content = re.sub(r'from app\.core\.config import', 'from ..core.config import', content)
        content = re.sub(r'from app\.core\.database import', 'from ..core.database import', content)
        content = re.sub(r'from app\.models\.', 'from ..models.', content)
        content = re.sub(r'from app\.schemas\.', 'from ..schemas.', content)
        content = re.sub(r'from app\.services\.', 'from ..services.', content)
        content = re.sub(r'from app\.auth\.', 'from ..auth.', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Corregido: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error en {file_path}: {e}")
        return False

def fix_imports_in_directory(directory):
    """Corregir importaciones en un directorio"""
    fixed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    # Corregir importaciones en el directorio src/app
    count = fix_imports_in_directory("src/app")
    print(f"Total archivos corregidos: {count}")
