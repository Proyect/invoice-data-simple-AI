# Guía de Migraciones de Base de Datos

## 📋 Resumen

Este proyecto usa **Alembic** para gestionar las migraciones de la base de datos PostgreSQL.

---

## 🚀 Inicio Rápido

### Windows
```batch
# Ejecutar script de inicialización
init-db.bat
```

### Manual
```bash
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Iniciar PostgreSQL con Docker
docker-compose up -d postgres

# 3. Aplicar migraciones
alembic upgrade head
```

---

## 📊 Estado Actual

### Tablas Creadas
- `documents` - Tabla principal de documentos
- `alembic_version` - Control de versiones de migraciones

### Campos de documents
```sql
id                - INTEGER (PK)
filename          - VARCHAR(255)
original_filename - VARCHAR(255)
file_path         - VARCHAR(500)
file_size         - INTEGER
mime_type         - VARCHAR(100)
raw_text          - TEXT
extracted_data    - JSONB  ← Importante: JSONB para PostgreSQL
confidence_score  - INTEGER
ocr_provider      - VARCHAR(50)
ocr_cost          - VARCHAR(20)
processing_time   - VARCHAR(20)
search_vector     - TSVECTOR  ← Para búsqueda full-text
created_at        - TIMESTAMP
updated_at        - TIMESTAMP
```

### Índices
- `documents_pkey` - Primary Key
- `ix_documents_filename` - Búsqueda por nombre
- `ix_documents_created_at` - Búsqueda por fecha
- `ix_documents_extracted_data_gin` - Búsqueda en JSONB (GIN)
- `ix_documents_search_vector_gin` - Búsqueda full-text (GIN)
- Y más...

---

## 🔧 Comandos Útiles

### Ver Estado Actual
```bash
alembic current
```

### Ver Historial
```bash
alembic history --verbose
```

### Crear Nueva Migración
```bash
# Autogenerar desde cambios en modelos
alembic revision --autogenerate -m "Descripción del cambio"

# Migración vacía (manual)
alembic revision -m "Descripción"
```

### Aplicar Migraciones
```bash
# Aplicar todas las pendientes
alembic upgrade head

# Aplicar una específica
alembic upgrade +1

# Ir a una revisión específica
alembic upgrade <revision_id>
```

### Deshacer Migraciones
```bash
# Deshacer la última
alembic downgrade -1

# Volver al inicio
alembic downgrade base

# Ir a una revisión específica
alembic downgrade <revision_id>
```

---

## 🗄️ Gestión de PostgreSQL

### Conectarse a PostgreSQL
```bash
# Vía Docker
docker exec -it invoice-data-simple-ai-postgres-1 psql -U postgres -d document_extractor

# Comandos útiles en psql:
\dt              # Listar tablas
\d documents     # Describir tabla documents
\di              # Listar índices
\q               # Salir
```

### Consultas SQL
```sql
-- Ver todos los documentos
SELECT id, filename, created_at FROM documents;

-- Buscar en JSONB
SELECT * FROM documents 
WHERE extracted_data @> '{"tipo_documento": "factura"}';

-- Búsqueda full-text
SELECT * FROM documents 
WHERE search_vector @@ to_tsquery('spanish', 'factura');
```

---

## 🐛 Troubleshooting

### Error: "relation documents does not exist"
```bash
# Aplicar migraciones
alembic upgrade head
```

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: PostgreSQL no conecta
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | findstr postgres

# Iniciar PostgreSQL
docker-compose up -d postgres

# Verificar puerto correcto en alembic.ini
# Debe ser: postgresql://postgres:postgres@localhost:5434/document_extractor
```

### Error: "data type json has no default operator class for access method gin"
**Solución**: El modelo debe usar `JSONB` no `JSON` para PostgreSQL.

```python
# CORRECTO
from sqlalchemy.dialects.postgresql import JSONB
extracted_data = Column(JSONB, nullable=True)

# INCORRECTO
from sqlalchemy import JSON
extracted_data = Column(JSON, nullable=True)
```

### Limpiar y Empezar de Nuevo
```bash
# 1. Eliminar tablas
docker exec invoice-data-simple-ai-postgres-1 psql -U postgres -d document_extractor -c "DROP TABLE IF EXISTS documents CASCADE; DROP TABLE IF EXISTS alembic_version CASCADE;"

# 2. Eliminar migraciones
del alembic\versions\*.py

# 3. Generar nueva migración
alembic revision --autogenerate -m "Initial migration"

# 4. Aplicar
alembic upgrade head
```

---

## 📝 Buenas Prácticas

### 1. Siempre Revisar Migraciones Generadas
```bash
# Después de generar
alembic revision --autogenerate -m "Descripción"

# Revisar el archivo generado en alembic/versions/
# Verificar que los cambios sean correctos
```

### 2. No Editar Migraciones Aplicadas
- Una vez aplicada una migración, NO editarla
- Crear una nueva migración con los cambios

### 3. Hacer Backup Antes de Migraciones Importantes
```bash
# Backup de PostgreSQL
docker exec invoice-data-simple-ai-postgres-1 pg_dump -U postgres document_extractor > backup.sql

# Restaurar
docker exec -i invoice-data-simple-ai-postgres-1 psql -U postgres document_extractor < backup.sql
```

### 4. Probar Migraciones en Desarrollo
- Siempre probar en desarrollo antes de producción
- Verificar upgrade y downgrade funcionan

---

## 🔄 Flujo de Trabajo

### Cuando Cambias un Modelo

1. **Modificar el modelo**
   ```python
   # Ejemplo: src/app/models/document.py
   class Document(Base):
       # Agregar nuevo campo
       new_field = Column(String(100), nullable=True)
   ```

2. **Generar migración**
   ```bash
   alembic revision --autogenerate -m "Add new_field to documents"
   ```

3. **Revisar migración generada**
   ```python
   # alembic/versions/xxxxx_add_new_field.py
   def upgrade():
       op.add_column('documents', sa.Column('new_field', ...))
   
   def downgrade():
       op.drop_column('documents', 'new_field')
   ```

4. **Aplicar migración**
   ```bash
   alembic upgrade head
   ```

5. **Verificar**
   ```bash
   docker exec invoice-data-simple-ai-postgres-1 psql -U postgres -d document_extractor -c "\d documents"
   ```

---

## 🌐 Ambientes

### Desarrollo (Local)
```ini
# alembic.ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5434/document_extractor
```

### Docker
```ini
# docker-compose.yml ya configura la variable
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/document_extractor
```

### Producción
```bash
# Usar variable de entorno
export DATABASE_URL="postgresql://user:password@host:5432/dbname"

# O modificar alembic.ini
```

---

## ✅ Verificación Post-Migración

```bash
# 1. Verificar estado
alembic current

# 2. Verificar tablas
docker exec invoice-data-simple-ai-postgres-1 psql -U postgres -d document_extractor -c "\dt"

# 3. Probar API
curl http://localhost:8005/health

# 4. Probar upload
curl -X POST "http://localhost:8005/api/v1/upload" \
  -F "file=@test.pdf" \
  -F "document_type=factura"
```

---

## 📚 Recursos

- [Documentación de Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Fecha**: 9 de octubre de 2025  
**Versión**: 1.0  
**Estado**: ✅ Migraciones funcionando correctamente

