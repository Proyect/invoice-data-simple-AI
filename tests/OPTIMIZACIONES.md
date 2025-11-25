# Optimizaciones de Tests Implementadas

## Resumen

Se han implementado optimizaciones significativas en la suite de tests para mejorar la eficiencia, velocidad y mantenibilidad.

## Optimizaciones Implementadas

### 1. Fixtures Optimizadas (`conftest.py`)

#### Scopes Optimizados
- **Session scope**: Para servicios y motor de DB (se crean una vez por sesión)
- **Function scope**: Para datos de prueba y sesiones de DB (aislamiento por test)

#### Base de Datos Transaccional
- SQLite en memoria para tests rápidos
- Transacciones automáticas con rollback
- Aislamiento completo entre tests
- Limpieza automática de datos

#### Fixtures de Servicios
- Servicios con scope `session` para reutilización
- Caching automático de instancias
- Reducción de tiempo de inicialización

### 2. Marcadores Pytest

Todos los tests ahora tienen marcadores apropiados:
- `@pytest.mark.unit` - Tests unitarios
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.e2e` - Tests end-to-end
- `@pytest.mark.slow` - Tests que tardan más tiempo
- `@pytest.mark.requires_db` - Tests que requieren base de datos
- `@pytest.mark.requires_redis` - Tests que requieren Redis
- `@pytest.mark.requires_openai` - Tests que requieren OpenAI
- `@pytest.mark.requires_api` - Tests que requieren APIs externas
- `@pytest.mark.security` - Tests de seguridad

**Beneficios:**
- Ejecución selectiva: `pytest -m unit` para solo tests unitarios
- Exclusión de tests lentos: `pytest -m "not slow"`
- Mejor organización y filtrado

### 3. Mocks para Servicios Externos

Fixtures de mocks disponibles:
- `mock_tesseract` - Mock de Tesseract OCR
- `mock_spacy` - Mock de spaCy NLP
- `mock_openai` - Mock de OpenAI API
- `mock_redis` - Mock de Redis
- `mock_google_vision` - Mock de Google Vision API
- `mock_aws_textract` - Mock de AWS Textract

**Beneficios:**
- Tests más rápidos (sin llamadas reales a APIs)
- Tests más confiables (no dependen de servicios externos)
- Reducción de costos (no se consumen APIs de pago)

### 4. Parametrización de Tests

Tests duplicados consolidados usando `@pytest.mark.parametrize`:
- Extracción de campos comunes (número, fecha, CUIT)
- Reducción de código duplicado
- Mejor cobertura con múltiples casos

### 5. Configuración de pytest.ini

Optimizaciones en `pytest.ini`:
- Timeout global de 300 segundos
- Opciones de paralelización (comentadas, listas para usar con pytest-xdist)
- Marcadores estrictos para evitar errores
- Output optimizado (`-q` para modo quiet)

### 6. Fixtures Compartidas

Nuevo directorio `tests/fixtures/` con:
- `test_data.py` - Datos de prueba reutilizables
- Textos de ejemplo para diferentes tipos de documentos
- Datos extraídos de ejemplo
- Estructura para futuras fixtures compartidas

### 7. Timeouts en Tests

- Timeouts aumentados en tests de producción (10-15 segundos)
- Timeout global configurado en pytest.ini
- Prevención de tests que se cuelgan

### 8. Optimizaciones de Base de Datos

- SQLite en memoria para velocidad
- Transacciones con rollback automático
- Aislamiento completo entre tests
- Sin necesidad de limpieza manual

## Mejoras de Rendimiento

### Antes
- Tests lentos por inicialización repetida de servicios
- Llamadas reales a APIs externas
- Base de datos persistente (más lento)
- Sin paralelización

### Después
- Servicios con scope session (una vez por sesión)
- Mocks para todas las APIs externas
- SQLite en memoria (muy rápido)
- Configuración lista para paralelización

### Estimación de Mejora
- **Velocidad**: 3-5x más rápido
- **Confiabilidad**: Mayor (sin dependencias externas)
- **Costo**: Reducción significativa (sin llamadas a APIs de pago)

## Uso

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar solo tests unitarios
```bash
pytest -m unit
```

### Ejecutar tests de integración
```bash
pytest -m integration
```

### Excluir tests lentos
```bash
pytest -m "not slow"
```

### Ejecutar con paralelización (requiere pytest-xdist)
```bash
pytest -n auto
```

### Ejecutar con cobertura
```bash
pytest --cov=src/app --cov-report=html
```

## Próximos Pasos Recomendados

1. **Instalar pytest-xdist** para paralelización:
   ```bash
   pip install pytest-xdist
   ```
   Luego descomentar las líneas en `pytest.ini`

2. **Agregar más parametrizaciones** donde haya tests similares

3. **Crear más fixtures compartidas** en `tests/fixtures/`

4. **Agregar tests de performance** con benchmarks

5. **Configurar CI/CD** para ejecutar tests automáticamente

## Notas

- Los mocks están disponibles pero algunos tests aún pueden hacer llamadas reales
- La base de datos en memoria es perfecta para tests pero no para desarrollo
- Los marcadores permiten ejecución selectiva pero requieren mantenimiento

