# Modo Flexible - Elige tu Método de Procesamiento 🎛️

## ✨ Nueva Funcionalidad

Ahora puedes **elegir** qué método usar para procesar tus documentos:

- ✅ **Método de OCR** (extracción de texto)
- ✅ **Método de Extracción** (análisis de datos)

## 🎯 Endpoint Flexible

```
POST /api/v1/upload-flexible
```

### **Parámetros:**

| Parámetro | Tipo | Opciones | Descripción |
|-----------|------|----------|-------------|
| `file` | File | - | Archivo PDF o imagen |
| `document_type` | String | factura, recibo, etc | Tipo de documento |
| `ocr_method` | String | tesseract, google_vision, aws_textract, auto | Método de OCR |
| `extraction_method` | String | regex, spacy, llm, hybrid, auto | Método de extracción |

## 📊 Métodos Disponibles

### **Métodos de OCR**

#### 1. **tesseract** (Disponible ahora)
```
✅ Disponible: Sí
💰 Costo: Gratis
📈 Precisión: 70-80%
⚡ Velocidad: Rápido
```

#### 2. **google_vision** (Requiere configuración)
```
❌ Disponible: No (requiere API key)
💰 Costo: $1.50 por 1000 imágenes
📈 Precisión: 95-98%
⚡ Velocidad: Medio
🔧 Requiere: GOOGLE_APPLICATION_CREDENTIALS en .env
```

#### 3. **aws_textract** (Requiere configuración)
```
❌ Disponible: No (requiere API keys)
💰 Costo: $1.50 por 1000 imágenes
📈 Precisión: 90-95%
⚡ Velocidad: Medio
🔧 Requiere: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en .env
```

#### 4. **auto** (Recomendado)
```
✅ Disponible: Sí
📝 Descripción: Selecciona automáticamente el mejor método
```

### **Métodos de Extracción**

#### 1. **regex** (Siempre disponible)
```
✅ Disponible: Sí
📝 Descripción: Patrones de expresiones regulares
📈 Precisión: 65-70%
⚡ Velocidad: Muy rápido
💰 Costo: Gratis
```

#### 2. **spacy** (Disponible ahora)
```
✅ Disponible: Sí
📝 Descripción: Procesamiento con spaCy NLP
📈 Precisión: 75-80%
⚡ Velocidad: Rápido
💰 Costo: Gratis
```

#### 3. **llm** (Requiere configuración)
```
❌ Disponible: No (requiere API key)
📝 Descripción: Extracción con GPT
📈 Precisión: 90-95%
⚡ Velocidad: Lento
💰 Costo: ~$0.002 por request
🔧 Requiere: OPENAI_API_KEY en .env
```

#### 4. **hybrid** (Recomendado)
```
✅ Disponible: Sí
📝 Descripción: Combina regex + spaCy
📈 Precisión: 80-85%
⚡ Velocidad: Rápido
💰 Costo: Gratis
```

#### 5. **auto** (Automático)
```
✅ Disponible: Sí
📝 Descripción: Selecciona el mejor método según configuración
```

## 🚀 Cómo Usar

### **Opción 1: Interfaz Web (Más Fácil)**

1. Abre: http://localhost:8006/docs
2. Busca `POST /api/v1/upload-flexible`
3. Click "Try it out"
4. Completa:
   - **file**: Selecciona tu factura
   - **document_type**: `factura`
   - **ocr_method**: `tesseract` o `auto`
   - **extraction_method**: `hybrid` o `auto`
5. Click "Execute"
6. ¡Ve los datos extraídos con info del método usado!

### **Opción 2: Con cURL**

```bash
curl -X POST "http://localhost:8006/api/v1/upload-flexible" \
  -F "file=@factura.pdf" \
  -F "document_type=factura" \
  -F "ocr_method=tesseract" \
  -F "extraction_method=hybrid"
```

### **Opción 3: PowerShell**

```powershell
$file = "C:\ruta\a\factura.pdf"

$form = @{
    file = Get-Item $file
    document_type = "factura"
    ocr_method = "tesseract"
    extraction_method = "hybrid"
}

$response = Invoke-WebRequest -Uri "http://localhost:8006/api/v1/upload-flexible" `
    -Method POST `
    -Form $form

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 📊 Ejemplo de Respuesta

```json
{
  "success": true,
  "document_id": 6,
  "filename": "20251008_114500_factura.pdf",
  "file_size": 125846,
  "metodos_usados": {
    "ocr": "tesseract",
    "extraccion": "hybrid_regex_spacy",
    "tiempo_total": "3.45s"
  },
  "ocr_result": {
    "text_length": 1523,
    "confidence": 0.75,
    "cost": 0.0
  },
  "extracted_data": {
    "numero_factura": "00003-00000001",
    "fecha": "22/03/2019",
    "emisor": "MI EMPRESA S.A.",
    "cuit": "20-12345678-9",
    "totales": {
      "total": "1210.00"
    }
  },
  "confidence": 82,
  "message": "Documento procesado exitosamente"
}
```

## 🎮 Combinaciones Recomendadas

### **Para Facturas Simples (Rápido y Gratis)**
```
OCR: tesseract
Extracción: hybrid
Precisión esperada: 75-80%
Costo: $0
```

### **Para Facturas Complejas (Máxima Precisión)**
```
OCR: google_vision
Extracción: llm
Precisión esperada: 90-95%
Costo: ~$0.0035 por factura
```

### **Modo Automático (Balanceado)**
```
OCR: auto
Extracción: auto
El sistema decide según configuración y complejidad
```

## 📋 Ver Métodos Disponibles

```bash
curl http://localhost:8006/api/v1/upload-flexible/methods
```

Esto te dirá qué métodos están disponibles según tu configuración actual.

## ⚙️ Configurar APIs Cloud (Opcional)

### **Para Google Vision**:

1. Crear proyecto en Google Cloud Console
2. Habilitar Vision API
3. Descargar credentials.json
4. Configurar en `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   ```

### **Para AWS Textract**:

1. Crear cuenta AWS
2. Obtener access keys
3. Configurar en `.env`:
   ```env
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   AWS_REGION=us-east-1
   ```

### **Para OpenAI (LLM)**:

1. Crear cuenta en OpenAI
2. Generar API key
3. Configurar en `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   ```

## 🎯 Casos de Uso

### **Caso 1: Desarrollo (Sin configurar APIs)**
```
✅ Usar: ocr_method=tesseract, extraction_method=hybrid
✅ Precisión: 75-80%
✅ Costo: $0
✅ Disponible: Ahora mismo
```

### **Caso 2: Producción (APIs configuradas)**
```
✅ Usar: ocr_method=auto, extraction_method=auto
✅ El sistema usa la mejor combinación disponible
✅ Máxima precisión con control de costos
```

### **Caso 3: Pruebas y Comparación**
```
✅ Probar con diferentes combinaciones
✅ Comparar resultados
✅ Elegir la mejor configuración para tu caso
```

## 💡 Tips

1. **Modo auto** es lo más conveniente
2. **Hybrid** da mejores resultados que métodos individuales
3. **LLM** es mejor para documentos complejos o no estructurados
4. **Tesseract** es suficiente para facturas bien impresas

---

**¡Ahora tienes control total sobre cómo procesar tus documentos!** 🎉

**Prueba ahora**: http://localhost:8006/docs → `POST /api/v1/upload-flexible`

