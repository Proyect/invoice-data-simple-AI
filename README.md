# Document Extractor API - Invoice Data Simple AI 🚀

Sistema completo de extracción de datos de facturas y documentos usando OCR y procesamiento inteligente.

## ⚡ Inicio Rápido con Docker (Recomendado)

### **Paso 1: Construir imágenes**
```bash
docker-compose build
```

### **Paso 2: Iniciar servicios**
```bash
docker-compose up -d
```

### **Paso 3: Acceder a la aplicación**
```
http://localhost:8006/docs
```

## 🌐 Puertos Configurados

| Servicio | Puerto | URL |
|----------|--------|-----|
| **API** | 8006 | http://localhost:8006 |
| **Documentación** | 8006 | http://localhost:8006/docs |
| **PostgreSQL** | 5433 | localhost:5433 |
| **Redis** | 6380 | localhost:6380 |
| **PgAdmin** | 5050 | http://localhost:5050 |

## 🎯 Características

- ✅ **OCR automático** con Tesseract (incluido en Docker)
- ✅ **Extracción inteligente** de datos de facturas
- ✅ **Soporte para PDF** e imágenes (JPG, PNG)
- ✅ **Base de datos PostgreSQL** con búsqueda full-text
- ✅ **Cache con Redis** para mejor performance
- ✅ **API REST** con FastAPI
- ✅ **Documentación automática** con Swagger
- ✅ **Procesamiento asíncrono** con workers

## 📊 Datos que Extrae

De facturas argentinas:
- Número de factura
- Fecha de emisión
- Emisor y receptor
- CUIT/CUIL
- Condición ante IVA
- Items y productos
- Montos (subtotal, IVA, total)
- Emails y teléfonos

## 🚀 Uso

### **Subir una factura**

**Interfaz web**:
1. Abre http://localhost:8006/docs
2. POST /api/v1/upload
3. Sube tu factura PDF o imagen
4. ¡Ve los datos extraídos automáticamente!

**cURL**:
```bash
curl -X POST "http://localhost:8006/api/v1/upload" \
  -F "file=@factura.pdf" \
  -F "document_type=factura"
```

### **Listar documentos procesados**
```bash
curl http://localhost:8006/api/v1/documents
```

### **Ver estadísticas**
```bash
curl http://localhost:8006/api/v1/documents/stats
```

## 🛠️ Comandos Útiles

```bash
# Ver logs
docker-compose logs -f app

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Ver estado
docker-compose ps

# Acceder al contenedor
docker-compose exec app /bin/bash
```

## 📚 Documentación Completa

- **`DOCKER-DEPLOYMENT.md`** - Guía completa de Docker
- **`DOCKER-PUERTOS.md`** - Detalle de puertos
- **`COMO-USAR-LA-API.md`** - Guía de uso de la API
- **`doc/README.md`** - Documentación técnica completa

## 🔧 Desarrollo Local (Alternativa)

Si prefieres desarrollo local sin Docker:

```bash
# Configurar entorno virtual
setup_venv.bat

# Iniciar aplicación
.venv\Scripts\activate
python start.py
```

**Nota**: Requiere instalar Tesseract y Poppler manualmente.

## 🐛 Troubleshooting

### **Puerto ya en uso**
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8007:8005"  # Usar 8007 en lugar de 8006
```

### **Ver logs de errores**
```bash
docker-compose logs app
```

### **Reinicio limpio**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📄 Licencia

MIT License

## 🤝 Contribuir

Ver `DEVELOPMENT-WORKFLOW.md` para el flujo de desarrollo.

---

**¡Disfruta extrayendo datos de facturas automáticamente!** 🎉

