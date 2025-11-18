#!/usr/bin/env python3
"""
Script de Conveniencia para Tests
=================================

Script para ejecutar tests desde la raíz del proyecto.
"""
import sys
from pathlib import Path

# Agregar tests al path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

if __name__ == "__main__":
    from run_tests import main
    exit(main())





