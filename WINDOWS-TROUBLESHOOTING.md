# Solución de Problemas en Windows 🪟

Guía para resolver errores comunes de instalación en Windows.

## 🚨 Error: "Getting requirements to build wheel did not run successfully"

Este error es común en Windows con librerías que requieren compilación. Aquí están las soluciones:

## 🔧 Solución 1: Script Automático

```bash
# Ejecuta el script de reparación
fix-installation-windows.bat
```

## 🔧 Solución 2: Instalación Manual Paso a Paso

### **Paso 1: Actualizar herramientas**
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Actualizar pip y herramientas
python -m pip install --upgrade pip
python -m pip install --upgrade wheel setuptools
```

### **Paso 2: Instalar dependencias básicas**
```bash
# Instalar FastAPI y dependencias principales
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.1
pip install sqlalchemy==2.0.23
pip install alembic==1.13.1
```

### **Paso 3: Instalar OCR básico**
```bash
# OCR básico (sin problemas de compilación)
pip install pytesseract==0.3.10
pip install pillow==10.1.0
```

### **Paso 4: Instalar herramientas de desarrollo**
```bash
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install black==23.11.0
pip install isort==5.12.0
```

### **Paso 5: Instalar spaCy**
```bash
python -m spacy download es_core_news_sm
```

### **Paso 6: Dependencias opcionales (intentar)**
```bash
# Estas pueden fallar, pero no son críticas
pip install pdf2image || echo "pdf2image no instalado (opcional)"
pip install redis || echo "redis no instalado (opcional)"
pip install pandas || echo "pandas no instalado (opcional)"
```

## 🔧 Solución 3: Usar requirements mínimos

```bash
# Usar archivo de dependencias mínimas
pip install -r requirements-venv-minimal.txt
```

## 🔧 Solución 4: Instalar Visual Studio Build Tools

Si los errores persisten, instala las herramientas de compilación:

1. **Descargar Visual Studio Build Tools**
   - Ve a: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Descarga "Build Tools for Visual Studio 2022"

2. **Instalar con componentes necesarios**
   - Selecciona "C++ build tools"
   - Incluye "Windows 10/11 SDK"
   - Incluye "CMake tools for Visual Studio"

3. **Reiniciar y reinstalar**
   ```bash
   # Reiniciar terminal
   .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements-venv-windows.txt
   ```

## 🔧 Solución 5: Usar conda (Alternativa)

Si pip sigue fallando, usa conda:

```bash
# Instalar conda si no lo tienes
# Descargar desde: https://docs.conda.io/en/latest/miniconda.html

# Crear entorno con conda
conda create -n document-extractor python=3.11
conda activate document-extractor

# Instalar dependencias con conda
conda install -c conda-forge fastapi uvicorn
conda install -c conda-forge sqlalchemy
conda install -c conda-forge pillow
conda install -c conda-forge pytesseract

# Instalar el resto con pip
pip install python-multipart pydantic python-dotenv
```

## 🚀 Verificar Instalación

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Verificar instalación
python -c "import fastapi, sqlalchemy; print('✅ Instalación exitosa')"

# Iniciar aplicación
python main.py
```

## 📋 Dependencias por Prioridad

### **Críticas (Deben instalarse)**
- ✅ fastapi
- ✅ uvicorn
- ✅ sqlalchemy
- ✅ pydantic
- ✅ python-dotenv
- ✅ pytesseract
- ✅ pillow

### **Importantes (Recomendadas)**
- 🔶 python-multipart
- 🔶 aiofiles
- 🔶 alembic
- 🔶 pytest

### **Opcionales (Pueden fallar)**
- 🔸 opencv-python
- 🔸 pdf2image
- 🔸 redis
- 🔸 pandas
- 🔸 google-cloud-vision
- 🔸 boto3

## 🎯 Configuración Mínima Funcional

Si solo quieres que funcione básicamente:

```bash
# Instalar solo lo esencial
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv pytesseract pillow

# Iniciar aplicación
python main.py
```

La aplicación funcionará con:
- ✅ API web
- ✅ Base de datos SQLite
- ✅ OCR básico con Tesseract
- ❌ Sin procesamiento asíncrono
- ❌ Sin cache Redis
- ❌ Sin APIs cloud

## 🚨 Errores Específicos y Soluciones

### **Error: "Microsoft Visual C++ 14.0 is required"**
```bash
# Instalar Visual Studio Build Tools
# O usar conda en lugar de pip
```

### **Error: "Failed building wheel for opencv-python"**
```bash
# Usar versión headless
pip install opencv-python-headless
```

### **Error: "Failed building wheel for numpy"**
```bash
# Instalar numpy desde conda
conda install numpy
# O usar versión precompilada
pip install numpy --only-binary=all
```

### **Error: "Tesseract not found"**
```bash
# Descargar Tesseract para Windows
# https://github.com/UB-Mannheim/tesseract/wiki
# Instalar y agregar al PATH
```

## 📞 Soporte Adicional

Si sigues teniendo problemas:

1. **Verificar versión de Python**
   ```bash
   python --version  # Debe ser 3.8+
   ```

2. **Limpiar cache de pip**
   ```bash
   pip cache purge
   ```

3. **Recrear entorno virtual**
   ```bash
   rmdir /s .venv
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. **Usar Docker como alternativa**
   ```bash
   # Si todo falla, usar Docker
   docker-compose up -d
   ```

---

**¡Con estas soluciones deberías poder instalar todo correctamente! 🚀**
