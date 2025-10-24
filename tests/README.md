# Estructura de Tests del Sistema

## Organización

Los tests están organizados en una estructura jerárquica que facilita la ejecución y mantenimiento:

```
tests/
├── unit/                    # Tests unitarios
│   ├── test_academic_documents.py
│   ├── test_improved_precision.py
│   └── test_dni_extraction.py
├── integration/             # Tests de integración
│   └── test_full_system.py
├── e2e/                     # Tests end-to-end
│   └── test_complete_workflow.py
├── fixtures/                # Datos de prueba
├── utils/                   # Utilidades para tests
├── conftest.py             # Configuración de pytest
└── run_all_tests.py        # Script maestro
```

## Tipos de Tests

### Tests Unitarios (`unit/`)
- **Propósito**: Probar componentes individuales en aislamiento
- **Cobertura**: Servicios específicos, funciones, clases
- **Ejemplos**: 
  - Extracción de documentos académicos
  - Validación de DNI argentinos
  - Precisión de algoritmos de extracción

### Tests de Integración (`integration/`)
- **Propósito**: Probar la interacción entre múltiples componentes
- **Cobertura**: Servicios trabajando juntos, flujos de datos
- **Ejemplos**:
  - Integración completa del sistema
  - Detección automática de tipos de documento
  - Rendimiento de servicios combinados

### Tests End-to-End (`e2e/`)
- **Propósito**: Probar el flujo completo del sistema
- **Cobertura**: Casos de uso completos, experiencia del usuario
- **Ejemplos**:
  - Carga y procesamiento de documentos
  - Manejo de errores en producción
  - Rendimiento bajo carga

## Ejecución de Tests

### Ejecutar todos los tests
```bash
python tests/run_all_tests.py
```

### Ejecutar tests específicos
```bash
# Tests unitarios
python tests/unit/test_academic_documents.py
python tests/unit/test_dni_extraction.py

# Tests de integración
python tests/integration/test_full_system.py

# Tests E2E
python tests/e2e/test_complete_workflow.py
```

### Ejecutar con pytest
```bash
# Todos los tests
pytest tests/

# Tests específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Con reporte detallado
pytest tests/ -v --tb=short
```

## Funcionalidades Probadas

### Documentos Soportados
- ✅ Facturas comerciales
- ✅ Recibos de pago
- ✅ Títulos académicos
- ✅ Certificados de cursos
- ✅ Diplomas de graduación
- ✅ Licencias profesionales
- ✅ DNI argentinos (tarjeta y libreta)
- ✅ Pasaportes argentinos

### Servicios Probados
- ✅ Extracción básica con regex
- ✅ Extracción inteligente con IA
- ✅ Extracción académica especializada
- ✅ Extracción de DNI especializada
- ✅ Validación universal de datos
- ✅ Detección automática de tipos

### Métricas de Calidad
- ✅ Precisión de extracción
- ✅ Velocidad de procesamiento
- ✅ Manejo de errores
- ✅ Validación de datos
- ✅ Rendimiento bajo carga

## Configuración

### Variables de Entorno
Los tests utilizan la configuración por defecto del sistema. Para tests específicos, se pueden configurar variables de entorno:

```bash
export DATABASE_URL="sqlite:///./data/test.db"
export SECRET_KEY="test-key"
```

### Fixtures Disponibles
- `basic_extraction_service`: Servicio de extracción básica
- `intelligent_extraction_service`: Servicio de extracción inteligente
- `academic_extraction_service`: Servicio de extracción académica
- `dni_extraction_service`: Servicio de extracción de DNI
- `validation_service`: Servicio de validación universal
- `sample_factura_text`: Texto de ejemplo de factura
- `sample_titulo_text`: Texto de ejemplo de título
- `sample_dni_text`: Texto de ejemplo de DNI
- `sample_certificado_text`: Texto de ejemplo de certificado

## Reportes

### Reporte de Ejecución
El script `run_all_tests.py` genera un reporte completo que incluye:
- Número de tests ejecutados
- Tests exitosos y fallidos
- Tasa de éxito
- Tiempo total de ejecución
- Detalles por test individual

### Métricas de Calidad
- **Precisión de extracción**: Porcentaje de campos extraídos correctamente
- **Velocidad de procesamiento**: Tiempo promedio por documento
- **Cobertura de tipos**: Porcentaje de tipos de documento soportados
- **Estabilidad**: Tasa de éxito en múltiples ejecuciones

## Mantenimiento

### Agregar Nuevos Tests
1. Crear archivo en la carpeta apropiada (`unit/`, `integration/`, `e2e/`)
2. Seguir convenciones de nomenclatura: `test_*.py`
3. Usar fixtures disponibles en `conftest.py`
4. Documentar casos de prueba específicos

### Actualizar Tests Existentes
1. Mantener compatibilidad con cambios en la API
2. Actualizar datos de prueba según nuevos formatos
3. Verificar que todos los tests sigan pasando
4. Actualizar documentación si es necesario

## Troubleshooting

### Problemas Comunes
- **ImportError**: Verificar que el path de `src/` esté configurado correctamente
- **Timeout**: Aumentar tiempo de espera para tests de rendimiento
- **MemoryError**: Reducir tamaño de datos de prueba para tests de carga

### Debugging
- Usar `pytest -v` para output detallado
- Usar `pytest --tb=long` para stack traces completos
- Usar `pytest -s` para ver prints de debug