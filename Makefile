.PHONY: help dev dev-venv prod stop build logs shell clean restart setup setup-venv install test

help: ## Mostrar ayuda
	@echo "🐳 Document Extractor API - Comandos disponibles"
	@echo ""
	@echo "🐍 Entorno Virtual:"
	@echo "  setup-venv     - Configurar entorno virtual"
	@echo "  dev-venv       - Iniciar con entorno virtual"
	@echo "  install        - Instalar dependencias en venv"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  setup          - Configurar con Docker"
	@echo "  dev            - Iniciar desarrollo con Docker"
	@echo "  prod           - Iniciar producción con Docker"
	@echo ""
	@echo "🔧 Utilidades:"
	@echo "  test           - Ejecutar tests"
	@echo "  format         - Formatear código"
	@echo "  lint           - Linting"
	@echo "  clean          - Limpiar"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ==================== ENTORNO VIRTUAL ====================

setup-venv: ## Configurar entorno virtual (primera vez)
	@echo "🐍 Configurando entorno virtual..."
	@chmod +x setup_venv.sh
	@./setup_venv.sh

install: ## Instalar dependencias en entorno virtual
	@echo "📚 Instalando dependencias..."
	@source .venv/bin/activate && pip install -r requirements-venv.txt
	@source .venv/bin/activate && python -m spacy download es_core_news_sm

dev-venv: ## Iniciar aplicación con entorno virtual
	@echo "🚀 Iniciando con entorno virtual..."
	@chmod +x start_venv.sh
	@./start_venv.sh

venv-shell: ## Abrir shell en entorno virtual
	@echo "🐍 Abriendo shell en entorno virtual..."
	@source .venv/bin/activate && bash

# ==================== DOCKER ====================

setup: ## Configurar proyecto con Docker (primera vez)
	@echo "🐳 Configurando proyecto con Docker..."
	@mkdir -p uploads outputs data logs ssl
	@touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep
	@cp env.example .env
	@docker-compose build
	@echo "✅ Configuración completada!"

dev: ## Iniciar en modo desarrollo con Docker
	@echo "🚀 Iniciando en modo desarrollo..."
	@docker-compose up -d
	@echo "✅ Aplicación disponible en http://localhost:8005"

prod: ## Iniciar en modo producción con Docker
	@echo "🚀 Iniciando en modo producción..."
	@docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Aplicación disponible en http://localhost"

stop: ## Detener contenedores
	@echo "⏹️ Deteniendo contenedores..."
	@docker-compose down

build: ## Construir imágenes Docker
	@echo "🔨 Construyendo imágenes..."
	@docker-compose build --no-cache

logs: ## Ver logs en tiempo real
	@docker-compose logs -f app

logs-worker: ## Ver logs del worker
	@docker-compose logs -f worker

logs-all: ## Ver logs de todos los servicios
	@docker-compose logs -f

shell: ## Abrir shell en el contenedor
	@docker-compose exec app /bin/bash

shell-db: ## Conectar a PostgreSQL
	@docker-compose exec postgres psql -U postgres -d document_extractor

clean: ## Limpiar contenedores e imágenes
	@echo "🧹 Limpiando..."
	@docker-compose down -v
	@docker system prune -f

restart: ## Reiniciar aplicación
	@echo "🔄 Reiniciando..."
	@docker-compose restart app

status: ## Ver estado de contenedores
	@docker-compose ps

stats: ## Ver estadísticas de la cola
	@curl -s http://localhost:8005/api/v1/queue/stats | jq

health: ## Verificar salud de la aplicación
	@curl -s http://localhost:8005/health | jq

info: ## Ver información del sistema
	@curl -s http://localhost:8005/info | jq

# ==================== DESARROLLO ====================

test: ## Ejecutar tests
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && pytest; \
	else \
		docker-compose exec app pytest; \
	fi

format: ## Formatear código
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && black src/ && isort src/; \
	else \
		docker-compose exec app black src/; \
		docker-compose exec app isort src/; \
	fi

lint: ## Ejecutar linting
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && flake8 src/; \
	else \
		docker-compose exec app flake8 src/; \
	fi

migrate: ## Ejecutar migraciones
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && alembic upgrade head; \
	else \
		docker-compose exec app alembic upgrade head; \
	fi

migration: ## Crear nueva migración
	@read -p "Descripción de la migración: " desc; \
	if [ -d ".venv" ]; then \
		source .venv/bin/activate && alembic revision --autogenerate -m "$$desc"; \
	else \
		docker-compose exec app alembic revision --autogenerate -m "$$desc"; \
	fi

# ==================== UTILIDADES ====================

backup: ## Hacer backup de la base de datos
	@docker-compose exec postgres pg_dump -U postgres document_extractor > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Restaurar backup de la base de datos
	@read -p "Archivo de backup: " file; \
	docker-compose exec -T postgres psql -U postgres document_extractor < $$file

quick-start: ## Inicio rápido del proyecto
	@chmod +x quick-start.sh && ./quick-start.sh

check-deps: ## Verificar dependencias del sistema
	@echo "🔍 Verificando dependencias..."
	@echo "Python: $$(python3 --version 2>/dev/null || echo 'No encontrado')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'No encontrado')"
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo 'No encontrado')"
	@echo "Tesseract: $$(tesseract --version 2>/dev/null || echo 'No encontrado')"

# ==================== MIGRACIÓN ====================

migrate-to-docker: ## Migrar de desarrollo local a Docker
	@echo "🔄 Migrando a Docker..."
	@chmod +x migrate-to-docker.sh
	@./migrate-to-docker.sh

back-to-local: ## Regresar de Docker a desarrollo local
	@echo "🔄 Regresando a desarrollo local..."
	@chmod +x back-to-local.sh
	@./back-to-local.sh