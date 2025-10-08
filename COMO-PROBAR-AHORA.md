# Cómo Probar la Aplicación - AHORA 🚀

## ✅ Estado Actual: APLICACIÓN FUNCIONANDO

```
✅ API corriendo en: http://localhost:8005
✅ Health check: OK
✅ Base de datos: SQLite funcionando
✅ Documentos subidos: 4 archivos
❌ Tesseract OCR: NO instalado (por eso no procesa)
```

## 🎯 Dos Opciones para Probar

### **Opción 1: Instalar Tesseract AHORA (5 minutos)**

Si quieres que funcione **completamente**, necesitas Tesseract:

1. **Descarga directa**:
   ```
   https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
   ```

2. **Instalar** (click, click, next, next, finish)
   - Marca "Spanish" en idiomas
   - Marca "Add to PATH"

3. **Verificar** (abre NUEVA PowerShell):
   ```bash
   tesseract --version
   ```

4. **Reiniciar app**:
   ```bash
   Get-Process python | Stop-Process -Force
   .venv\Scripts\activate
   python start.py
   ```

5. **Probar**: http://localhost:8005/docs

### **Opción 2: Probar SIN Tesseract (AHORA MISMO)**

Puedes probar la API aunque Tesseract no esté instalado:

#### **A. Ver Documentación Interactiva**

```
Abre en tu navegador: http://localhost:8005/docs
```

Verás todos los endpoints disponibles.

#### **B. Ver Documentos Subidos**

```bash
# En PowerShell
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/documents"
```

O en navegador:
```
http://localhost:8005/api/v1/documents
```

#### **C. Ver un Documento Específico**

```bash
# Ver documento ID 1
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/documents/1"
```

#### **D. Intentar Subir una Factura (Verás el Error de Tesseract)**

```bash
# En navegador
http://localhost:8005/docs
# POST /api/v1/upload
# Try it out
# Sube una factura
# Verás: "tesseract is not installed"
```

## 🧪 Pruebas Disponibles AHORA

### **1. Health Check**
```bash
curl http://localhost:8005/health
# Resultado: {"status":"healthy","port":8005}
```

### **2. Info de la API**
```bash
curl http://localhost:8005/
# Verás: endpoints disponibles, features, versión
```

### **3. Test de OCR**
```bash
curl http://localhost:8005/api/v1/upload/test
# Resultado: {"error":"tesseract is not installed"}
```

### **4. Listar Documentos**
```bash
curl http://localhost:8005/api/v1/documents
# Verás: los 4 documentos que subiste
```

### **5. Ver Documento Específico**
```bash
curl http://localhost:8005/api/v1/documents/4
# Verás: detalles del documento
```

### **6. Ver Estadísticas**
```bash
curl http://localhost:8005/api/v1/documents/stats
# Verás: estadísticas de documentos procesados
```

## 📊 Tus Archivos Subidos

Ya tienes 4 archivos en el sistema:

| ID | Archivo | Tamaño | Estado |
|----|---------|--------|--------|
| 4 | 20296451143_011_00002_00000014.pdf | 86 KB | Sin procesar |
| 3 | Boleta-Pago.pdf | 120 KB | Error (endpoint incorrecto) |
| 2 | test_invoice.jpg | 78 KB | Sin procesar |
| 1 | Boleta-Pago.pdf | 120 KB | Error (endpoint incorrecto) |

## 🚀 Cuando Instales Tesseract

Podrás reprocesar estos documentos:

```bash
# Reprocesar documento
curl -X POST "http://localhost:8005/api/v1/documents/2/reprocess"
```

O subir nuevos:

```bash
# Subir nuevo documento
curl -X POST "http://localhost:8005/api/v1/upload" \
  -F "file=@factura.pdf" \
  -F "document_type=factura"
```

## 🎯 Prueba Paso a Paso (CON Tesseract instalado)

```bash
# 1. Verificar Tesseract
tesseract --version

# 2. Reiniciar app
Get-Process python | Stop-Process -Force
.venv\Scripts\activate
python start.py

# 3. Esperar 10 segundos
Start-Sleep -Seconds 10

# 4. Probar con factura
$file = "C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data-simple-AI\uploads\20251007_155000_test_invoice.jpg"

$form = @{
    file = Get-Item $file
    document_type = "factura"
}

Invoke-WebRequest -Uri "http://localhost:8005/api/v1/upload" -Method POST -Form $form
```

## 📖 Documentación Completa

Todos los archivos creados para ayudarte:

1. **`GUIA-RAPIDA-INICIO.md`** ← Empieza aquí
2. **`INSTALL-TESSERACT.md`** ← Instalar Tesseract
3. **`COMO-USAR-LA-API.md`** ← Cómo usar
4. **`TEST-FACTURA-EJEMPLO.md`** ← Probar con tu factura
5. **`SOLUCION-ERRORES.md`** ← Errores comunes
6. **`RESUMEN-FINAL.md`** ← Este archivo

## 🎉 Resultado Final Esperado

Después de instalar Tesseract:

```json
{
  "success": true,
  "document_id": 5,
  "filename": "20251007_161234_test_invoice.jpg",
  "extracted_data": {
    "tipo_documento": "factura",
    "numero_factura": "00003-00000001",
    "fecha": "22/03/2019",
    "codigo": "COD 011",
    "condicion_iva": "Responsable Monotributo",
    "totales": {
      "subtotal": "0.00",
      "total": "0.00"
    }
  },
  "confidence": 75,
  "message": "Documento procesado exitosamente"
}
```

---

**ACCIÓN INMEDIATA**: Instala Tesseract OCR  
**TIEMPO**: 5 minutos  
**RESULTADO**: Sistema funcionando al 100%

**Link de descarga**: https://github.com/UB-Mannheim/tesseract/wiki

¡Estás a 5 minutos de tener todo funcionando! 🎉


