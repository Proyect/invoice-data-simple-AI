# Cómo Usar la API - Guía Rápida

## 🚨 Error Actual

Si ves: `"Error subiendo archivo: cannot pickle 'thread.lock' object"`

**Causa**: Estás usando el endpoint incorrecto (`/upload-async` o `/upload-optimized`)

## ✅ Solución: Usar el Endpoint Correcto

### **Endpoint Correcto: `/api/v1/upload`**

Este endpoint es **simple** y **funciona sin Redis ni APIs externas**.

## 🚀 Cómo Subir una Factura

### **Opción 1: Interfaz Web (Más Fácil)**

1. Abre en tu navegador:
   ```
   http://localhost:8005/docs
   ```

2. Busca la sección **"upload-simple"** (NO "upload-optimized" ni "upload-async")

3. Click en `POST /api/v1/upload` ← **Este es el correcto**

4. Click en "Try it out"

5. Click en "Choose File" y selecciona tu factura PDF

6. (Opcional) En `document_type` escribe "factura"

7. Click en "Execute"

8. ¡Verás los datos extraídos!

### **Opción 2: Con cURL**

```bash
curl -X POST "http://localhost:8005/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@C:/ruta/a/tu/factura.pdf" \
  -F "document_type=factura"
```

### **Opción 3: Con PowerShell**

```powershell
$form = @{
    file = Get-Item "C:\ruta\a\tu\factura.pdf"
    document_type = "factura"
}

Invoke-WebRequest -Uri "http://localhost:8005/api/v1/upload" `
    -Method POST `
    -Form $form
```

## 📋 Endpoints Disponibles

| Endpoint | Estado | Requiere |
|----------|--------|----------|
| `/api/v1/upload` | ✅ **USAR ESTE** | Solo Tesseract |
| `/api/v1/upload-optimized` | ⚠️ Requiere APIs | Google Vision + OpenAI |
| `/api/v1/upload-async` | ❌ No usar | Redis configurado |

## 🎯 Respuesta Esperada

Cuando subes una factura exitosamente:

```json
{
  "success": true,
  "document_id": 1,
  "filename": "20251007_154530_factura.pdf",
  "file_size": 125846,
  "text_length": 1523,
  "extracted_data": {
    "tipo_documento": "factura",
    "numero_factura": "0001-00001234",
    "fecha": "07/10/2025",
    "emisor": "MI EMPRESA S.A.",
    "receptor": "CLIENTE XYZ",
    "cuit": "20-12345678-9",
    "totales": {
      "subtotal": "1000.00",
      "iva": "210.00",
      "total": "1210.00"
    }
  },
  "confidence": 75,
  "message": "Documento procesado exitosamente"
}
```

## ⚠️ Errores Comunes

### Error: "tesseract is not installed"

**Solución**: Instala Tesseract OCR
- Ver: `INSTALL-TESSERACT.md`
- Descarga: https://github.com/UB-Mannheim/tesseract/wiki

### Error: "cannot pickle 'thread.lock' object"

**Solución**: Estás usando el endpoint incorrecto
- ❌ NO uses: `/upload-async` o `/upload-optimized`  
- ✅ USA: `/upload` (simple)

### Error: "Tipo de archivo no soportado"

**Solución**: Solo se aceptan:
- PDF (`.pdf`)
- Imágenes: JPEG (`.jpg`, `.jpeg`), PNG (`.png`), TIFF (`.tiff`)

## 🔍 Verificar que Todo Funciona

```bash
# 1. Verificar que la API responde
curl http://localhost:8005/health

# 2. Verificar Tesseract
curl http://localhost:8005/api/v1/upload/test

# 3. Ver documentación
# Abrir: http://localhost:8005/docs
```

## 💡 Tips

1. **Calidad de imagen**: Usa PDFs o imágenes claras (300 DPI mínimo)
2. **Tamaño de archivo**: Máximo 10 MB recomendado
3. **Idioma**: El OCR está configurado para español
4. **Tipo de documento**: Especifica "factura", "recibo" o "boleta"

## 📞 Si Sigue Sin Funcionar

1. **Ver logs de la aplicación**:
   - Mira la consola donde ejecutaste `python main.py`
   - Busca mensajes de error en rojo

2. **Reiniciar la aplicación**:
   ```bash
   # Detener
   Get-Process python | Stop-Process -Force
   
   # Esperar 3 segundos
   Start-Sleep -Seconds 3
   
   # Iniciar
   python main.py
   ```

3. **Verificar archivos de configuración**:
   - Verifica que existe `.env`
   - Verifica que existe carpeta `uploads/`

---

**¿Necesitas más ayuda?** Revisa `SOLUCION-MODELO.md` o `INSTALL-TESSERACT.md`

