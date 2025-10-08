# Document Extractor API - Entorno Virtual 🐍

Guía completa para configurar y ejecutar el proyecto usando un **entorno virtual de Python** en lugar de Docker.

## 🚀 Inicio Rápido

### **Opción 1: Script Automático**

**Linux/Mac:**
```bash
chmod +x quick-start-venv.sh
./quick-start-venv.sh
```

**Windows:**
```bash
quick-start-venv.bat
```

### **Opción 2: Comandos Manuales**

```bash
# 1. Configurar entorno virtual
make setup-venv

# 2. Iniciar aplicación
make dev-venv
```

### **Opción 3: Paso a Paso**

```bash
# 1. Crear entorno virtual
python3 -m venv .venv

# 2. Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements-venv.txt

# 4. Instalar spaCy
python -m spacy download es_core_news_sm

# 5. Configurar variables
cp env-venv.example .env

# 6. Iniciar aplicación
python main.py
```

## 📋 Prerrequisitos

### **Obligatorios**
- ✅ **Python 3.8+** instalado
- ✅ **pip** actualizado

### **Opcionales (para mejor funcionalidad)**
- 🔧 **Tesseract OCR** - Para OCR local
- 🗄️ **PostgreSQL** - Para base de datos avanzada
- 🔄 **Redis** - Para cache y procesamiento asíncrono

## 🛠️ Instalación de Prerrequisitos

### **Tesseract OCR**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar en `C:\Program Files\Tesseract-OCR\`
3. Agregar al PATH o configurar en `.env`

### **PostgreSQL (Opcional)**

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb document_extractor
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb document_extractor
```

**Windows:**
1. Descargar desde: https://www.postgresql.org/download/windows/
2. Instalar y crear base de datos

### **Redis (Opcional)**

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
1. Descargar desde: https://github.com/microsoftarchive/redis/releases
2. Instalar y ejecutar

## ⚙️ Configuración

### **Variables de Entorno**

El archivo `.env` se crea automáticamente desde `env-venv.example`. Puedes editarlo:

```env
# Base de datos - SQLite por defecto
DATABASE_URL=sqlite:///./data/documents.db

# Para PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/document_extractor

# Tesseract (si no está en PATH)
# Windows: TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
# Linux/Mac: TESSERACT_CMD=tesseract

# APIs Cloud (opcional)
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=AKIA...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## 🎯 Comandos Útiles

### **Gestión del Entorno Virtual**

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Desactivar entorno virtual
deactivate

# Verificar instalación
pip list

# Actualizar dependencias
pip install --upgrade -r requirements-venv.txt
```

### **Comandos Make**

```bash
# Configuración
make setup-venv          # Configurar entorno virtual
make install             # Instalar dependencias

# Desarrollo
make dev-venv            # Iniciar con entorno virtual
make venv-shell          # Abrir shell en venv

# Utilidades
make test                # Ejecutar tests
make format              # Formatear código
make lint                # Linting
make check-deps          # Verificar dependencias
```

### **Scripts Directos**

```bash
# Configuración
./setup_venv.sh          # Linux/Mac
setup_venv.bat           # Windows

# Inicio
./start_venv.sh          # Linux/Mac
start_venv.bat           # Windows

# Inicio rápido
./quick-start-venv.sh    # Linux/Mac
quick-start-venv.bat     # Windows
```

## 🔄 Modos de Funcionamiento

### **Modo Básico (Solo Python)**
- ✅ **SQLite** como base de datos
- ✅ **Tesseract** para OCR
- ✅ **FastAPI** para API
- ❌ Sin cache Redis
- ❌ Sin procesamiento asíncrono

### **Modo Completo (Con dependencias)**
- ✅ **PostgreSQL** como base de datos
- ✅ **Redis** para cache y colas
- ✅ **OCR híbrido** (Google Vision + Tesseract)
- ✅ **Procesamiento asíncrono**
- ✅ **LLMs** para extracción

## 📊 Comparación: Entorno Virtual vs Docker

| Aspecto | Entorno Virtual | Docker |
|---------|----------------|---------|
| **Configuración** | Más simple | Más completa |
| **Dependencias** | Instalar manualmente | Automáticas |
| **Portabilidad** | Limitada | Completa |
| **Rendimiento** | Nativo | Virtualizado |
| **Desarrollo** | Más rápido | Más robusto |
| **Producción** | Requiere setup | Listo para deploy |

## 🚀 Uso de la API

### **Iniciar Aplicación**

```bash
# Con entorno virtual activado
python main.py

# O usando make
make dev-venv
```

### **Endpoints Disponibles**

```bash
# Health check
curl http://localhost:8005/health

# Documentación
# Abrir: http://localhost:8005/docs

# Subir documento
curl -X POST "http://localhost:8005/api/v1/upload-optimized" \
     -F "file=@documento.pdf" \
     -F "document_type=factura"
```

## 🐛 Troubleshooting

### **Error: Python no encontrado**
```bash
# Verificar instalación
python3 --version
python --version

# Instalar Python 3.8+
# Ubuntu: sudo apt install python3 python3-pip python3-venv
# macOS: brew install python3
# Windows: Descargar desde python.org
```

### **Error: Módulo no encontrado**
```bash
# Verificar entorno virtual activado
which python  # Linux/Mac
where python  # Windows

# Reinstalar dependencias
pip install -r requirements-venv.txt
```

### **Error: Tesseract no encontrado**
```bash
# Verificar instalación
tesseract --version

# Configurar en .env
TESSERACT_CMD=/usr/bin/tesseract  # Linux
TESSERACT_CMD=/opt/homebrew/bin/tesseract  # macOS
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows
```

### **Error: Base de datos**
```bash
# Verificar PostgreSQL
psql --version

# O usar SQLite por defecto
DATABASE_URL=sqlite:///./data/documents.db
```

### **Error: Redis**
```bash
# Verificar Redis
redis-cli ping

# La aplicación funciona sin Redis (modo básico)
```

## 📁 Estructura del Proyecto

```
invoice-data-simple-AI/
├── .venv/                   # Entorno virtual
├── src/                     # Código fuente
├── uploads/                 # Archivos subidos
├── outputs/                 # Resultados
├── data/                    # Base de datos SQLite
├── logs/                    # Logs
├── setup_venv.sh            # Script configuración Linux/Mac
├── setup_venv.bat           # Script configuración Windows
├── start_venv.sh            # Script inicio Linux/Mac
├── start_venv.bat           # Script inicio Windows
├── quick-start-venv.sh      # Inicio rápido Linux/Mac
├── quick-start-venv.bat     # Inicio rápido Windows
├── requirements-venv.txt    # Dependencias para venv
├── env-venv.example         # Variables de entorno ejemplo
├── Makefile                 # Comandos útiles
└── README-VENV.md          # Esta documentación
```

## 🔧 Desarrollo

### **Activar Entorno para Desarrollo**

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias de desarrollo
pip install -r requirements-venv.txt

# Formatear código
black src/
isort src/

# Linting
flake8 src/

# Tests
pytest
```

### **Agregar Dependencias**

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar nueva dependencia
pip install nueva-dependencia

# Actualizar requirements
pip freeze > requirements-venv.txt
```

## 🚀 Migración a Producción

### **Usar Docker para Producción**

```bash
# Cambiar a Docker para producción
make setup      # Configurar Docker
make prod       # Iniciar en modo producción
```

### **Deploy con Entorno Virtual**

```bash
# En servidor de producción
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-venv.txt
python main.py
```

## 📞 Soporte

- **Documentación**: http://localhost:8005/docs
- **Health Check**: http://localhost:8005/health
- **Info del Sistema**: http://localhost:8005/info

---

**¡Disfruta desarrollando con entorno virtual! 🐍✨**
