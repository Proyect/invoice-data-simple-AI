# Guía Rápida de Inicio 🚀

## ✅ Estado Actual

**Aplicación**: ✅ Corriendo en http://localhost:8005  
**Base de Datos**: ✅ SQLite funcionando  
**Problema**: ❌ Tesseract OCR NO instalado

## 🚨 Problema Actual

Los documentos subidos no se procesan porque **falta Tesseract OCR**:

```
Documentos subidos: 4
Procesados correctamente: 0
Con errores: 4
```

**Causa**: Tesseract OCR no está instalado en tu sistema.

## ✅ Solución en 3 Pasos

### **Paso 1: Instalar Tesseract OCR (5 minutos)**

1. **Descargar el instalador**:
   - Abre: https://github.com/UB-Mannheim/tesseract/wiki
   - Busca: "tesseract-ocr-w64-setup-5.x.x.exe"
   - Descarga la última versión (64-bit)

2. **Ejecutar el instalador**:
   - Doble click en el archivo descargado
   - Click "Next"
   - **IMPORTANTE**: En la pantalla de componentes, selecciona:
     - ✅ "Additional Language Data"
     - ✅ "Spanish" o "Español"
   - **IMPORTANTE**: Marca "Add to PATH" si aparece la opción
   - Instalar en: `C:\Program Files\Tesseract-OCR` (por defecto está bien)
   - Click "Install"

3. **Verificar instalación**:
   - Abre una **NUEVA** ventana de PowerShell
   - Ejecuta:
     ```bash
     tesseract --version
     ```
   - Deberías ver algo como: `tesseract 5.3.0`

### **Paso 2: Reiniciar la Aplicación**

```bash
# En PowerShell (en la carpeta del proyecto)
cd C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data-simple-AI

# Detener aplicación
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Activar entorno virtual e iniciar
.venv\Scripts\activate
python start.py
```

### **Paso 3: Probar con tu Factura**

**Opción A: Interfaz Web (Recomendado)**

1. Abre en el navegador:
   ```
   http://localhost:8005/docs
   ```

2. Busca la sección **"upload-simple"**

3. Click en `POST /api/v1/upload` (el que dice "Upload document")

4. Click en "Try it out"

5. Click en "Choose File" y selecciona tu factura:
   ```
   uploads\20251007_155000_test_invoice.jpg
   ```

6. En `document_type` escribe: `factura`

7. Click en "Execute"

8. ¡Verás todos los datos extraídos!

**Opción B: Con PowerShell**

```powershell
$factura = "C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data-simple-AI\uploads\20251007_155000_test_invoice.jpg"

$form = @{
    file = Get-Item $factura
    document_type = "factura"
}

$response = Invoke-WebRequest -Uri "http://localhost:8005/api/v1/upload" `
    -Method POST `
    -Form $form

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 📊 Datos que Debería Extraer de tu Factura

De la factura de prueba que tienes, debería extraer:

- ✅ **Tipo**: Factura C
- ✅ **Número**: COD 011 - Punto de Venta: 00003 - Comp Nro: 00000001
- ✅ **Fecha de Emisión**: 22/03/2019
- ✅ **Período Facturado**: 22/03/2019 - 22/03/2019
- ✅ **Condición frente al IVA**: Responsable Monotributo / Consumidor Final
- ✅ **Condición de venta**: Contado
- ✅ **Cantidad**: 1.00 unidades
- ✅ **Subtotal**: $0.00
- ✅ **Otros Tributos**: $0.00
- ✅ **Total**: $0.00 (parece ser una factura de ejemplo)

## 🎯 Ejemplo de Respuesta Esperada

Una vez que Tesseract esté instalado:

```json
{
  "success": true,
  "document_id": 5,
  "filename": "20251007_160000_test_invoice.jpg",
  "file_size": 78666,
  "text_length": 523,
  "extracted_data": {
    "tipo_documento": "factura",
    "numero_factura": "00003-00000001",
    "fecha": "22/03/2019",
    "condicion_iva": "Responsable Monotributo",
    "totales": {
      "subtotal": "0.00",
      "total": "0.00"
    }
  },
  "confidence": 60,
  "message": "Documento procesado exitosamente"
}
```

## ⚠️ Si Tesseract Ya Está Instalado pero No Funciona

### **Opción 1: Configurar Ruta Manualmente**

Edita el archivo `.env`:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Luego reinicia la aplicación.

### **Opción 2: Agregar al PATH**

1. Buscar "Variables de entorno" en Windows
2. Editar "Path" en Variables del sistema
3. Agregar: `C:\Program Files\Tesseract-OCR`
4. Guardar y **reiniciar PowerShell**

## 🔍 Verificar que Todo Funciona

### **1. Verificar Tesseract**:
```bash
tesseract --version
```

### **2. Verificar la Aplicación**:
```bash
curl http://localhost:8005/api/v1/upload/test
```

Debería mostrar:
```json
{
  "tesseract_version": "5.3.0",
  "spacy_loaded": true,
  "status": "OK"
}
```

### **3. Probar Upload**:
- Abre: http://localhost:8005/docs
- Usa `POST /api/v1/upload`
- Sube una factura

## 📞 Enlaces de Descarga

- **Tesseract para Windows**: https://github.com/UB-Mannheim/tesseract/wiki
- **Instalador directo**: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

## 💡 Tip

Después de instalar Tesseract, **cierra y abre una nueva terminal** para que reconozca el PATH.

---

**¿Ya instalaste Tesseract?** ¡Perfecto! Reinicia la app y prueba con tu factura. 🎉


