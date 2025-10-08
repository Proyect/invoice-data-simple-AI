# Prueba de la Factura Ejemplo 📄

## 📋 Factura de Prueba Analizada

He visto tu factura de ejemplo: `20251007_155000_test_invoice.jpg`

### **Datos Visibles en la Factura:**

```
TIPO: Factura C (ORIGINAL)
CÓDIGO: COD 011

Punto de Venta: 00003
Comp. Nro: 00000001
Fecha de Emisión: 22/03/2019

Razón Social: [No visible en la imagen]
Domicilio Comercial: [No visible]
Condición frente al IVA: Responsable Monotributo

Período Facturado Desde: 22/03/2019
Hasta: 22/03/2019
Fecha de Vto. para el pago: 22/03/2019

Condición frente al IVA: Consumidor Final
Condición de venta: Contado

Cantidad: 1.00 unidades
Precio Unit.: 0.00
Imp. Bonif: 0.00
Subtotal: $ 0.00

Importe Otros Tributos: $ 0.00
Importe Total: $ 0.00

CAE Nº: [Visible]
Fecha de Vto. de CAE: [Visible]
```

## ✅ Datos que Debería Extraer el Sistema

Una vez que Tesseract esté instalado, el sistema debería extraer:

```json
{
  "tipo_documento": "factura",
  "subtipo": "Factura C",
  "codigo": "COD 011",
  "numero_factura": "00003-00000001",
  "punto_venta": "00003",
  "numero": "00000001",
  
  "fechas": {
    "emision": "22/03/2019",
    "periodo_desde": "22/03/2019",
    "periodo_hasta": "22/03/2019",
    "vencimiento_pago": "22/03/2019"
  },
  
  "condicion_iva": {
    "emisor": "Responsable Monotributo",
    "receptor": "Consumidor Final"
  },
  
  "condicion_venta": "Contado",
  
  "items": [
    {
      "cantidad": "1.00",
      "unidad": "unidades",
      "precio_unitario": "0.00",
      "bonificacion": "0.00",
      "subtotal": "0.00"
    }
  ],
  
  "totales": {
    "subtotal": "0.00",
    "otros_tributos": "0.00",
    "total": "0.00"
  },
  
  "cae": {
    "numero": "[Visible en imagen]",
    "vencimiento": "[Visible en imagen]"
  }
}
```

## 🧪 Cómo Probar Ahora

### **Sin Tesseract (Actual)**

❌ No funciona - Obtienes:
```json
{
  "error": "tesseract is not installed"
}
```

### **Con Tesseract (Después de Instalar)**

✅ Funciona perfectamente:

```bash
# 1. Abre la documentación
http://localhost:8005/docs

# 2. Ve a POST /api/v1/upload

# 3. Sube la factura: uploads\20251007_155000_test_invoice.jpg

# 4. Verás algo como:
{
  "success": true,
  "document_id": 5,
  "filename": "20251007_161234_test_invoice.jpg",
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
  "confidence": 65
}
```

## 🚀 Pasos Siguientes

### **1. Instalar Tesseract**

**Link directo al instalador**:
```
https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
```

**Durante la instalación**:
- ✅ Selecciona "Additional Language Data"
- ✅ Marca "Spanish"
- ✅ Marca "Add to PATH" (si aparece)

### **2. Verificar Instalación**

Abre **NUEVA** terminal PowerShell:
```bash
tesseract --version
```

### **3. Reiniciar la Aplicación**

```bash
# Detener
Get-Process python | Stop-Process -Force

# Esperar
Start-Sleep -Seconds 3

# Iniciar
.venv\Scripts\activate
python start.py
```

### **4. Verificar que Tesseract Funciona**

```bash
# Debería mostrar la versión de Tesseract
curl http://localhost:8005/api/v1/upload/test
```

### **5. Subir la Factura**

**Opción A: Interfaz Web**
```
1. Abre: http://localhost:8005/docs
2. POST /api/v1/upload
3. Try it out
4. Choose File: uploads\20251007_155000_test_invoice.jpg
5. document_type: factura
6. Execute
```

**Opción B: PowerShell**
```powershell
$file = "C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data-simple-AI\uploads\20251007_155000_test_invoice.jpg"

$form = @{
    file = Get-Item $file
    document_type = "factura"
}

$response = Invoke-WebRequest -Uri "http://localhost:8005/api/v1/upload" -Method POST -Form $form
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 📊 Qué Esperar

Una vez instalado Tesseract, al subir la factura deberías ver:

```json
{
  "success": true,
  "document_id": 5,
  "extracted_data": {
    "tipo_documento": "factura",
    "numero_factura": "00003-00000001",
    "fecha": "22/03/2019",
    "condicion_iva": "Responsable Monotributo",
    "condicion_venta": "Contado",
    "totales": {
      "subtotal": "0.00",
      "otros_tributos": "0.00",
      "total": "0.00"
    }
  },
  "confidence": 60-80,
  "message": "Documento procesado exitosamente"
}
```

## ⚠️ Notas Importantes

1. **Reinicia PowerShell** después de instalar Tesseract
2. **Usa el endpoint correcto**: `/api/v1/upload` (NO `/upload-async`)
3. **Formatos soportados**: PDF, JPG, PNG, TIFF
4. **Tamaño máximo**: 10 MB

## 🎯 Checklist

- [ ] Tesseract instalado
- [ ] Tesseract en el PATH
- [ ] Aplicación reiniciada
- [ ] Test OCR pasa: http://localhost:8005/api/v1/upload/test
- [ ] Factura subida exitosamente

## 📞 Si Sigue Sin Funcionar

1. **Verifica Tesseract**:
   ```bash
   tesseract --version
   ```

2. **Si no funciona, configura manualmente**:
   Edita `.env`:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

3. **Reinicia TODO**:
   - Cierra PowerShell
   - Abre nueva PowerShell
   - Activa venv
   - Inicia app

---

**¿Listo?** Instala Tesseract y probemos tu factura! 🚀


