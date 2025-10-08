# Instalación de Tesseract OCR para Windows

## 🚨 Problema Actual

La aplicación no puede extraer texto de documentos porque **Tesseract OCR no está instalado**.

## ✅ Solución: Instalar Tesseract OCR

### **Opción 1: Instalador para Windows (Recomendado)**

1. **Descargar Tesseract OCR**:
   - Ve a: https://github.com/UB-Mannheim/tesseract/wiki
   - Descarga el instalador más reciente (64-bit): `tesseract-ocr-w64-setup-5.x.x.exe`

2. **Instalar**:
   - Ejecuta el instalador
   - **IMPORTANTE**: Marca la opción para agregar al PATH
   - Instala en la ruta por defecto: `C:\Program Files\Tesseract-OCR`

3. **Seleccionar idioma español**:
   - Durante la instalación, en "Additional Language Data"
   - Marca "Spanish" o "Español"

4. **Verificar instalación**:
   ```bash
   # Abrir nueva terminal (PowerShell)
   tesseract --version
   ```

### **Opción 2: Configurar manualmente si no está en el PATH**

Si instalaste Tesseract pero no funciona:

1. Edita el archivo `.env`:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

2. Reinicia la aplicación:
   ```bash
   # Detener
   Get-Process python | Stop-Process -Force
   
   # Iniciar
   python main.py
   ```

### **Opción 3: Usar Chocolatey (si lo tienes)**

```bash
choco install tesseract
```

## 🧪 Verificar que Funciona

1. **Verificar desde PowerShell**:
   ```bash
   tesseract --version
   ```

2. **Probar en la aplicación**:
   ```bash
   # Abrir en el navegador
   http://localhost:8005/api/v1/upload/test
   ```

   Deberías ver:
   ```json
   {
     "tesseract_version": "5.x.x",
     "spacy_loaded": true,
     "status": "OK"
   }
   ```

## 🚀 Después de Instalar Tesseract

1. **Reiniciar la aplicación**:
   ```bash
   # Detener procesos de Python
   Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
   
   # Iniciar nuevamente
   python main.py
   ```

2. **Probar con un documento**:
   - Abre: http://localhost:8005/docs
   - Ve a `POST /api/v1/upload`
   - Sube una factura (PDF o imagen)
   - Verás los datos extraídos automáticamente

## 📊 Qué Datos Extrae la Aplicación

Con Tesseract instalado, la aplicación puede extraer:

- ✅ **Número de factura**
- ✅ **Fecha**
- ✅ **Nombre del emisor**
- ✅ **Nombre del receptor/cliente**
- ✅ **CUIT/CUIL**
- ✅ **Montos y totales**
- ✅ **Items/productos**
- ✅ **Condición ante IVA**
- ✅ **Emails y teléfonos**

## ⚠️ Troubleshooting

### Error: "tesseract is not installed"

1. Verifica que Tesseract está instalado:
   ```bash
   tesseract --version
   ```

2. Si da error, reinstala Tesseract y marca "Add to PATH"

3. O configura manualmente en `.env`:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

### Error: "Failed loading language 'spa'"

Tesseract no tiene el idioma español instalado:

1. Descarga el archivo de idioma:
   - https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata

2. Cópialo a:
   - `C:\Program Files\Tesseract-OCR\tessdata\spa.traineddata`

3. Reinicia la aplicación

## 💡 Alternativas si No Puedes Instalar Tesseract

Si por alguna razón no puedes instalar Tesseract, puedes usar solo las APIs cloud:

1. Configurar Google Vision API o AWS Textract en `.env`
2. Usar el endpoint `/api/v1/upload-optimized` (requiere APIs configuradas)

---

**¿Necesitas ayuda?** Revisa la documentación completa en `doc/README.md`

