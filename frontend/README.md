# Document Extractor Frontend

Frontend React para el sistema de extracción de documentos con IA.

## Características

- **Dashboard**: Vista general del sistema con estadísticas
- **Subida de Documentos**: Interfaz para cargar documentos con múltiples opciones
- **Lista de Documentos**: Visualización y gestión de documentos procesados
- **API Integration**: Comunicación completa con el backend FastAPI

## Tecnologías

- React 18
- Ant Design (UI Components)
- Axios (HTTP Client)
- React Router (Navegación)
- Nginx (Servidor web)

## Estructura del Proyecto

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Layout principal con navegación
│   │   ├── Dashboard.jsx       # Dashboard con estadísticas
│   │   ├── DocumentUpload.jsx  # Componente de subida
│   │   └── DocumentList.jsx    # Lista de documentos
│   ├── services/
│   │   └── api.js              # Servicio API
│   ├── App.jsx                 # Componente principal
│   ├── index.js                # Punto de entrada
│   └── index.css               # Estilos globales
├── Dockerfile                  # Configuración Docker
├── nginx.conf                  # Configuración Nginx
└── package.json                # Dependencias
```

## Instalación Local

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm start

# Construir para producción
npm run build
```

## Docker

```bash
# Construir imagen
docker build -t document-extractor-frontend .

# Ejecutar contenedor
docker run -p 3000:80 document-extractor-frontend
```

## Endpoints del Frontend

- **Dashboard**: `/` - Vista principal con estadísticas
- **Subir Documento**: `/upload` - Interfaz de carga
- **Lista de Documentos**: `/documents` - Gestión de documentos

## Configuración

El frontend se conecta al backend a través de la variable de entorno:

```env
REACT_APP_API_URL=http://localhost:8006
```

## Funcionalidades

### Dashboard
- Estadísticas del sistema
- Estado de servicios
- Accesos rápidos

### Subida de Documentos
- **Método Simple**: Tesseract + spaCy
- **Método Flexible**: Selección de OCR y extracción
- Soporte para PDF, JPG, PNG, TIFF
- Validación de archivos

### Lista de Documentos
- Vista tabular con paginación
- Búsqueda de documentos
- Detalles completos de cada documento
- Visualización de datos extraídos

## Desarrollo

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm start

# Ejecutar tests
npm test

# Construir para producción
npm run build
```

El frontend se ejecutará en `http://localhost:3001` y se conectará automáticamente al backend en `http://localhost:8006`.
