# Document Extractor API - Sistema de Producción

## 🚀 Sistema Profesional de Procesamiento de Documentos con IA

Sistema completo de extracción, análisis y gestión de documentos con tecnologías modernas y arquitectura profesional.

### ✨ Características Principales

- **🔐 Autenticación JWT** - Sistema seguro de usuarios con tokens
- **📄 Upload de Archivos** - Soporte para PDF, JPG, PNG, TIFF
- **🔍 OCR Avanzado** - Extracción de texto con múltiples proveedores
- **🧠 Análisis Inteligente** - IA para extracción de datos estructurados
- **🔎 Búsqueda Avanzada** - Filtros, paginación y búsqueda semántica
- **📊 Estadísticas** - Métricas y análisis del sistema en tiempo real
- **👑 Panel de Administración** - Gestión completa del sistema
- **📚 Documentación Automática** - Swagger/OpenAPI integrado

### 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **Pydantic v2** - Validación de datos robusta
- **SQLAlchemy** - ORM para base de datos
- **SQLite/PostgreSQL** - Base de datos
- **JWT** - Autenticación segura
- **Python 3.8+** - Lenguaje principal

### 📋 Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- 2GB RAM mínimo
- 1GB espacio en disco

### 🔧 Instalación y Configuración

#### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd invoice-data-simple-AI
```

#### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

#### 4. Iniciar el sistema
```bash
python start_production.py
```

### 🚀 Uso del Sistema

#### Iniciar Servidor
```bash
python start_production.py
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

#### Ejecutar Pruebas
```bash
python test_production_system.py
```

### 📚 Documentación de la API

#### Endpoints Principales

##### 🔐 Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Información del usuario actual

##### 📄 Documentos
- `GET /api/v2/documents/` - Listar documentos
- `POST /api/v2/documents/upload` - Subir documento
- `GET /api/v2/documents/{id}` - Obtener documento
- `PUT /api/v2/documents/{id}` - Actualizar documento
- `DELETE /api/v2/documents/{id}` - Eliminar documento
- `POST /api/v2/documents/search` - Búsqueda avanzada

##### ⚙️ Procesamiento
- `POST /api/v2/documents/{id}/process` - Procesar documento

##### 📊 Estadísticas
- `GET /api/v2/documents/stats/overview` - Estadísticas del sistema

##### 👑 Administración
- `GET /admin/users` - Listar usuarios (admin)
- `GET /admin/database/info` - Info de base de datos (admin)

##### 🔧 Sistema
- `GET /` - Información del sistema
- `GET /health` - Health check
- `GET /info` - Info detallada del sistema

### 📖 Ejemplos de Uso

#### 1. Registrar Usuario
```python
import requests

response = requests.post("http://localhost:8000/auth/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Usuario de Prueba",
    "password": "securepassword123"
})
```

#### 2. Autenticarse
```python
response = requests.post("http://localhost:8000/auth/login", json={
    "username_or_email": "testuser",
    "password": "securepassword123"
})

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

#### 3. Subir Documento
```python
files = {"file": open("document.pdf", "rb")}
data = {"document_type": "invoice"}

response = requests.post(
    "http://localhost:8000/api/v2/documents/upload",
    files=files,
    data=data,
    headers=headers
)
```

#### 4. Procesar Documento
```python
response = requests.post(
    f"http://localhost:8000/api/v2/documents/{document_id}/process",
    headers=headers
)
```

#### 5. Buscar Documentos
```python
search_data = {
    "query": "invoice",
    "document_type": "pdf",
    "page": 1,
    "size": 10
}

response = requests.post(
    "http://localhost:8000/api/v2/documents/search",
    json=search_data,
    headers=headers
)
```

### 🏗️ Arquitectura del Sistema

```
src/app/
├── main.py                 # Aplicación principal FastAPI
├── core/                   # Configuración central
│   ├── config.py          # Configuraciones del sistema
│   └── database.py        # Configuración de base de datos
├── models/                 # Modelos SQLAlchemy
│   ├── document.py        # Modelo de documentos
│   └── user.py           # Modelo de usuarios
├── schemas/               # Schemas Pydantic
│   ├── document_enhanced.py  # Schemas de documentos
│   └── user_enhanced_simple.py  # Schemas de usuarios
├── auth/                  # Sistema de autenticación
│   ├── dependencies.py   # Dependencias de autenticación
│   ├── jwt_handler.py    # Manejo de JWT
│   └── password_handler.py  # Manejo de contraseñas
├── routes/               # Rutas de la API
└── services/             # Servicios de negocio
```

### 🔒 Seguridad

- **Autenticación JWT** con tokens seguros
- **Validación de datos** con Pydantic v2
- **Hashing de contraseñas** con bcrypt
- **CORS configurado** para desarrollo
- **Validación de archivos** por tipo y tamaño
- **Logging de seguridad** completo

### 📊 Monitoreo y Logs

- **Logging estructurado** con niveles configurables
- **Health checks** para monitoreo
- **Métricas de sistema** en tiempo real
- **Trazabilidad** de operaciones
- **Archivos de log** organizados por fecha

### 🚀 Despliegue en Producción

#### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Docker (Opcional)
```bash
docker-compose up -d
```

#### Nginx (Recomendado)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 🧪 Testing

El sistema incluye pruebas automatizadas completas:

```bash
python test_production_system.py
```

**Cobertura de pruebas:**
- ✅ Endpoints del sistema
- ✅ Autenticación JWT
- ✅ CRUD de documentos
- ✅ Upload de archivos
- ✅ Búsqueda avanzada
- ✅ Procesamiento de documentos
- ✅ Manejo de errores
- ✅ Estadísticas del sistema

### 📈 Rendimiento

- **Respuesta rápida** con FastAPI
- **Paginación** para listas grandes
- **Caché** de consultas frecuentes
- **Procesamiento asíncrono** para tareas pesadas
- **Optimización** de consultas SQL

### 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

### 🆘 Soporte

Para soporte técnico o preguntas:
- 📧 Email: support@example.com
- 📚 Documentación: http://localhost:8000/docs
- 🐛 Issues: GitHub Issues

### 🎯 Roadmap

- [ ] Integración con más proveedores de OCR
- [ ] Dashboard web con React
- [ ] Procesamiento en lote
- [ ] API de webhooks
- [ ] Integración con servicios en la nube
- [ ] Machine Learning avanzado

---

**Versión:** 2.0.0  
**Última actualización:** Octubre 2024  
**Estado:** ✅ Producción Ready











