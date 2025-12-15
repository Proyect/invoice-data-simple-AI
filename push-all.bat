@echo off
REM Script para hacer push a ambos repositorios remotos (GitHub y UCASAL)
REM Uso: push-all.bat [branch]
REM Ejemplo: push-all.bat main

setlocal

REM Obtener la rama del argumento o usar 'main' por defecto
if "%1"=="" (
    set BRANCH=main
) else (
    set BRANCH=%1
)

echo ========================================
echo Push Multi-Remote - GitHub y UCASAL
echo ========================================
echo.
echo Rama: %BRANCH%
echo.

REM Verificar que estamos en un repositorio Git
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encuentra un repositorio Git en este directorio.
    exit /b 1
)

REM Verificar que la rama existe localmente
git rev-parse --verify %BRANCH% >nul 2>&1
if errorlevel 1 (
    echo ERROR: La rama '%BRANCH%' no existe localmente.
    echo Ramas disponibles:
    git branch
    exit /b 1
)

echo [1/2] Haciendo push a GitHub (origin)...
git push origin %BRANCH%
if errorlevel 1 (
    echo.
    echo ERROR: Fallo el push a GitHub. Continuando con UCASAL...
    set GITHUB_ERROR=1
) else (
    echo ✓ Push a GitHub exitoso
    set GITHUB_ERROR=0
)

echo.
echo [2/2] Haciendo push a UCASAL...
git push ucasal %BRANCH%
if errorlevel 1 (
    echo.
    echo ERROR: Fallo el push a UCASAL.
    set UCASAL_ERROR=1
) else (
    echo ✓ Push a UCASAL exitoso
    set UCASAL_ERROR=0
)

echo.
echo ========================================
echo Resumen:
echo ========================================
if %GITHUB_ERROR%==0 (
    echo GitHub:  ✓ Exitoso
) else (
    echo GitHub:  ✗ Fallo
)

if %UCASAL_ERROR%==0 (
    echo UCASAL:  ✓ Exitoso
) else (
    echo UCASAL:  ✗ Fallo
)

echo.

REM Si ambos fallaron, salir con código de error
if %GITHUB_ERROR%==1 if %UCASAL_ERROR%==1 (
    echo ERROR: Ambos pushes fallaron.
    exit /b 1
)

REM Si al menos uno fue exitoso, salir con éxito
exit /b 0

