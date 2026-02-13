# Guía de Actualización de Dependencias

## Estado Actual

Las dependencias están en versiones relativamente recientes. Esta guía proporciona un proceso para verificar y actualizar dependencias de forma segura.

## Proceso de Actualización

### 1. Verificar Versiones Actuales

```bash
# Verificar versiones instaladas
pip list

# Verificar versiones en requirements.txt
cat requirements.txt
```

### 2. Verificar Versiones Disponibles

```bash
# Para cada paquete, verificar última versión
pip index versions fastapi
pip index versions uvicorn
pip index versions sqlalchemy
pip index versions pydantic
```

### 3. Actualizar de Forma Incremental

**NO actualizar todas las dependencias a la vez.** Actualizar en grupos relacionados:

#### Grupo 1: FastAPI y Servidor
```bash
# Verificar compatibilidad
fastapi==0.115.0  # Verificar última versión estable
uvicorn[standard]==0.32.0  # Verificar última versión
python-multipart==0.0.12
```

#### Grupo 2: Base de Datos
```bash
sqlalchemy==2.0.36  # Ya está actualizado
alembic==1.13.1  # Verificar si hay actualizaciones
psycopg2-binary==2.9.9  # Verificar última versión
```

#### Grupo 3: Pydantic
```bash
pydantic[email]==2.10.6  # Verificar compatibilidad con código
pydantic-settings==2.1.0  # Verificar compatibilidad
```

#### Grupo 4: OCR y Procesamiento
```bash
pytesseract==0.3.10
pillow>=10.0.0
pdf2image==1.16.3
opencv-python-headless==4.10.0.84
numpy>=2.0.0
```

#### Grupo 5: Cloud APIs
```bash
google-cloud-vision==3.4.4
boto3==1.34.0
openai==1.3.0  # Verificar última versión (cambios frecuentes)
```

#### Grupo 6: Testing
```bash
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

### 4. Probar Después de Cada Actualización

```bash
# 1. Actualizar requirements.txt
# 2. Reinstalar dependencias
pip install -r requirements.txt

# 3. Ejecutar tests
pytest tests/ -v

# 4. Verificar que la aplicación inicia
python main.py
```

### 5. Verificar Compatibilidad

**Problemas Comunes**:

1. **Pydantic v2**: Asegurar que todo el código usa Pydantic v2 APIs
2. **SQLAlchemy 2.0**: Verificar que queries usan sintaxis 2.0
3. **FastAPI**: Verificar que endpoints siguen funcionando
4. **OpenAI**: API cambia frecuentemente, verificar breaking changes

## Dependencias Críticas

### FastAPI
- **Actual**: 0.104.1
- **Última**: Verificar en PyPI
- **Notas**: Cambios menores entre versiones, generalmente compatible

### SQLAlchemy
- **Actual**: 2.0.36
- **Última**: Verificar en PyPI
- **Notas**: Ya en versión 2.0, actualizaciones menores

### Pydantic
- **Actual**: 2.10.6
- **Última**: Verificar en PyPI
- **Notas**: Ya en v2, verificar compatibilidad con código existente

### OpenAI
- **Actual**: 1.3.0
- **Última**: Verificar en PyPI
- **Notas**: API cambia frecuentemente, revisar changelog

## Recomendaciones

1. **Actualizar en Ambiente de Desarrollo Primero**
   - Probar todas las funcionalidades
   - Ejecutar suite completa de tests
   - Verificar que no hay regresiones

2. **Mantener Versiones Fijas en Producción**
   - No usar `>=` en producción
   - Fijar versiones exactas
   - Documentar cambios

3. **Usar Virtual Environments**
   - Aislar dependencias por proyecto
   - Facilitar rollback si es necesario

4. **Documentar Cambios**
   - Mantener CHANGELOG
   - Documentar breaking changes
   - Actualizar README si es necesario

## Script de Verificación

```bash
#!/bin/bash
# verify_dependencies.sh

echo "Verificando dependencias..."

# Verificar que todas las dependencias están instaladas
pip check

# Ejecutar tests
pytest tests/ -v --tb=short

# Verificar que la app inicia
python -c "from src.app.main import app; print('App loads successfully')"

echo "Verificación completa"
```

## Automatización

Considerar usar herramientas como:
- **Dependabot** (GitHub): Actualizaciones automáticas de dependencias
- **Renovate**: Similar a Dependabot
- **pip-audit**: Verificar vulnerabilidades de seguridad

## Notas de Seguridad

1. **Actualizar Regularmente**: Dependencias desactualizadas pueden tener vulnerabilidades
2. **Revisar Changelogs**: Especialmente para paquetes de seguridad
3. **Probar Thoroughly**: No asumir compatibilidad automática
4. **Mantener Backup**: Poder hacer rollback si es necesario

## Estado Actual de Dependencias

Las dependencias actuales están en versiones relativamente recientes y estables. No hay necesidad urgente de actualizar, pero se recomienda:

1. Verificar actualizaciones de seguridad mensualmente
2. Actualizar dependencias menores trimestralmente
3. Actualizar dependencias mayores después de testing exhaustivo


































