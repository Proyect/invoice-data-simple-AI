#!/bin/bash
# Script para hacer push a ambos repositorios remotos (GitHub y UCASAL)
# Uso: ./push-all.sh [branch]
# Ejemplo: ./push-all.sh main

# Obtener la rama del argumento o usar 'main' por defecto
BRANCH=${1:-main}

echo "========================================"
echo "Push Multi-Remote - GitHub y UCASAL"
echo "========================================"
echo ""
echo "Rama: $BRANCH"
echo ""

# Verificar que estamos en un repositorio Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "ERROR: No se encuentra un repositorio Git en este directorio."
    exit 1
fi

# Verificar que la rama existe localmente
if ! git rev-parse --verify "$BRANCH" > /dev/null 2>&1; then
    echo "ERROR: La rama '$BRANCH' no existe localmente."
    echo "Ramas disponibles:"
    git branch
    exit 1
fi

# Variables para tracking de errores
GITHUB_ERROR=0
UCASAL_ERROR=0

# Push a GitHub
echo "[1/2] Haciendo push a GitHub (origin)..."
if git push origin "$BRANCH"; then
    echo "✓ Push a GitHub exitoso"
else
    echo ""
    echo "ERROR: Fallo el push a GitHub. Continuando con UCASAL..."
    GITHUB_ERROR=1
fi

echo ""

# Push a UCASAL
echo "[2/2] Haciendo push a UCASAL..."
if git push ucasal "$BRANCH"; then
    echo "✓ Push a UCASAL exitoso"
else
    echo ""
    echo "ERROR: Fallo el push a UCASAL."
    UCASAL_ERROR=1
fi

echo ""
echo "========================================"
echo "Resumen:"
echo "========================================"

if [ $GITHUB_ERROR -eq 0 ]; then
    echo "GitHub:  ✓ Exitoso"
else
    echo "GitHub:  ✗ Fallo"
fi

if [ $UCASAL_ERROR -eq 0 ]; then
    echo "UCASAL:  ✓ Exitoso"
else
    echo "UCASAL:  ✗ Fallo"
fi

echo ""

# Si ambos fallaron, salir con código de error
if [ $GITHUB_ERROR -eq 1 ] && [ $UCASAL_ERROR -eq 1 ]; then
    echo "ERROR: Ambos pushes fallaron."
    exit 1
fi

# Si al menos uno fue exitoso, salir con éxito
exit 0

