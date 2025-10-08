# Solución: Problema con Extracción de Datos

## 🚨 Problema Identificado

La aplicación no puede extraer datos de las facturas porque **falta Tesseract OCR**.

## ✅ Solución Rápida

### **Paso 1: Instalar Tesseract OCR**

1. Descarga: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecuta el instalador: `tesseract-ocr-w64-setup-5.x.x.exe`
3. **IMPORTANTE**: Marca "Add to PATH" durante la instalación
4. Selecciona idioma "Spanish" en "Additional Language Data"

### **Paso 2: Reiniciar la Aplicación**

```bash
# Abrir PowerShell en la carpeta del proyecto
.venv\Scripts\activate

# Detener procesos anteriores
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Iniciar aplicación
python main.py
```

### **Paso 3: Verificar que Funciona**

```bash
# Abrir en el navegador
http://localhost:8005/api/v1/upload/test

# Deberías ver algo como:
{
  "tesseract_version": "5.3.0",
  "spacy_loaded": true,
  "status": "OK"
}
```

## 🎯 Cómo Usar la Aplicación

### **Opción 1: Interfaz Web (Más Fácil)**

1. Abre en tu navegador:
   ```
   http://localhost:8005/docs
   ```

2. Ve a la sección `upload-simple`

3. Click en `POST /api/v1/upload`

4. Click en "Try it out"

5. Sube tu factura (PDF o imagen)

6. Click en "Execute"

7. **¡Verás todos los datos extraídos!**

### **Opción 2: Con PowerShell**

```powershell
# Preparar el archivo
$file = "C:\ruta\a\tu\factura.pdf"

# Subir documento
Invoke-WebRequest -Uri "http://localhost:8005/api/v1/upload" `
    -Method POST `
    -Form @{
        file = Get-Item $file
        document_type = "factura"
    }
```

## 📊 Datos que Extrae

La aplicación extrae automáticamente:

### **De Facturas:**
- ✅ Número de factura
- ✅ Fecha
- ✅ Emisor (nombre de la empresa)
- ✅ Receptor (cliente)
- ✅ CUIT/CUIL
- ✅ Montos (subtotal, IVA, total)
- ✅ Items/productos
- ✅ Condición ante IVA

### **De Recibos:**
- ✅ Número de recibo
- ✅ Fecha
- ✅ Emisor
- ✅ Receptor
- ✅ Monto
- ✅ Concepto

### **Datos Generales:**
- ✅ Emails
- ✅ Teléfonos
- ✅ Fechas
- ✅ Personas mencionadas
- ✅ Organizaciones

## 🔧 Ejemplo de Respuesta

Cuando subes una factura, obtienes algo como:

```json
{
  "success": true,
  "document_id": 1,
  "filename": "20251007_151234_factura.pdf",
  "extracted_data": {
    "tipo_documento": "factura",
    "numero_factura": "0001-00001234",
    "fecha": "07/10/2025",
    "emisor": "DISTRIBUIDORA ANDINA S.A.",
    "receptor": "Juan Pérez",
    "cuit": "20-12345678-9",
    "condicion_iva": "Responsable Inscripto",
    "totales": {
      "subtotal": "1000.00",
      "iva": "210.00",
      "total": "1210.00"
    },
    "items": [
      {
        "cantidad": "10",
        "descripcion": "Producto A",
        "precio": "100.00"
      }
    ]
  },
  "confidence": 85,
  "message": "Documento procesado exitosamente"
}
```

## 🎓 Mejoras del Modelo

El nuevo servicio de extracción (`BasicExtractionService`) usa:

1. **spaCy** - Para reconocimiento de entidades
2. **Regex avanzados** - Patrones específicos para facturas argentinas
3. **Múltiples estrategias** - Diferentes patrones para encontrar los mismos datos
4. **Validación inteligente** - Detecta automáticamente el tipo de documento

## ⚠️ Si Tesseract No Funciona

### **Verificar Instalación:**
```bash
tesseract --version
```

### **Configurar Ruta Manualmente:**
Edita `.env`:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### **Ver Logs:**
```bash
# Los logs mostrarán qué está pasando
# Busca en la consola donde ejecutaste python main.py
```

## 💡 Tips para Mejores Resultados

1. **Calidad de imagen**: Usa imágenes claras y bien iluminadas
2. **Resolución**: Mínimo 300 DPI para PDFs
3. **Formato**: PDF o JPG/PNG funcionan mejor
4. **Tamaño**: Facturas completas, no recortes
5. **Idioma**: El modelo está optimizado para español

## 🚀 Próximos Pasos

Una vez que Tesseract funcione:

1. **Probar con varias facturas** para ver la precisión
2. **Ajustar patrones** si hay campos específicos que no extrae
3. **Configurar APIs cloud** (opcional) para mejor precisión
4. **Migrar a Docker** cuando quieras producción

---

**¿Todo funcionando?** ¡Perfecto! Ya puedes procesar tus facturas automáticamente. 🎉

