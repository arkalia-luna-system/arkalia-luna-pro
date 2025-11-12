# 📦 Makefile Arkalia IA Devstation - Enhanced

.PHONY: all test format bump patch minor major zeroia clean install dev-setup security-check performance-check docs-build docker-build docker-test

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Commandes principales
all: test

# 🧪 Tests
test:
	@echo "🧪 Exécution des tests complets..."
	bash ./scripts/shell/ark-test-full.sh

test-unit:
	@echo "🧪 Tests unitaires uniquement..."
	pytest tests/unit/ -v --cov=modules --cov-report=term-missing

test-integration:
	@echo "🧪 Tests d'intégration..."
	pytest tests/integration/ -v

test-e2e:
	@echo "🧪 Tests end-to-end..."
	pytest tests/e2e/ -v

# 🎨 Formatage et linting
format:
	@echo "🎨 Formatage du code..."
	@find . -name "._*.py" -type f -delete || true
	black . --exclude archive/ --exclude "._*"
	ruff check . --fix --exclude archive/ --exclude "._*"
	# isort .  # DÉSACTIVÉ - cause des problèmes

format-check:
	@echo "🔍 Vérification du formatage..."
	@find . -name "._*.py" -type f -delete || true
	black --check --diff . --exclude archive/ --exclude "._*"
	ruff check . --exclude archive/ --exclude "._*"
	# isort --check-only --diff .  # DÉSACTIVÉ - cause des problèmes

# 🧹 Nettoyage
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -name "._*" -delete
	find . -name ".DS_Store" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# 📦 Installation et setup
install:
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt

dev-setup:
	@echo "🔧 Setup environnement de développement..."
	$(PIP) install -r requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

# 🔒 Sécurité
security-check:
	@echo "🔒 Vérification de sécurité..."
	bandit -r modules/ -f json -o bandit-report.json
	safety check --output html > safety-report.html

# ⚡ Performance
performance-check:
	@echo "⚡ Tests de performance..."
	pytest tests/performance/ -v

# 📚 Documentation
docs-build:
	@echo "📚 Construction de la documentation..."
	mkdocs build

docs-serve:
	@echo "📚 Serveur de documentation..."
	mkdocs serve

# 🐳 Docker
docker-build:
	@echo "🐳 Construction des images Docker..."
	$(DOCKER_COMPOSE) build

docker-test:
	@echo "🐳 Tests Docker..."
	$(DOCKER_COMPOSE) up -d
	sleep 10
	curl -f http://localhost:8000/health || exit 1
	$(DOCKER_COMPOSE) down

# 🚀 Lancement rapide
run:
	@echo "🚀 Lancement Arkalia-LUNA..."
	$(DOCKER_COMPOSE) -f docker-compose.yml up --build

# 🧪 Tests avec couverture
test:
	@echo "🧪 Tests avec couverture..."
	pytest --cov=modules --cov-report=term-missing --cov-report=html

docker-clean:
	@echo "🐳 Nettoyage Docker..."
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

# 🔄 Gestion des versions
bump:
	bumpver update

patch:
	bumpver update --patch

minor:
	bumpver update --minor

major:
	bumpver update --major

# 🎯 ZeroIA spécifique
zeroia:
	@echo "🔁 [Make] ZeroIA full check"
	@$(DOCKER_COMPOSE) ps -a | grep zeroia
	@$(DOCKER_COMPOSE) inspect zeroia --format="Status: {{.State.Status}} | Restarting: {{.State.Restarting}}"
	@$(DOCKER_COMPOSE) logs zeroia --tail 30
	@ruff modules/zeroia/ --fix
	@black modules/zeroia/
	@pytest tests/unit/test_state_writer.py
	@ls -lh modules/zeroia/state/zeroia_state.toml
	@ls -lh state/zeroia_dashboard.json
	@echo "✅ [Make] Fin ZeroIA full check"

# 🔍 Vérifications
check-all: format-check security-check test
	@echo "✅ Toutes les vérifications passées!"

# 📊 Rapports
coverage-report:
	@echo "📊 Rapport de couverture..."
	pytest --cov=modules --cov-report=html --cov-report=term-missing
	@echo "📊 Rapport généré dans htmlcov/"

# 🚀 Déploiement
deploy-check:
	@echo "🚀 Vérification pré-déploiement..."
	check-all
	docker-clean
	docker-build
	docker-test

# Aide
help:
	@echo "📦 Makefile Arkalia IA Devstation - Commandes disponibles:"
	@echo ""
	@echo "🧪 Tests:"
	@echo "  test          - Tests complets"
	@echo "  test-unit     - Tests unitaires"
	@echo "  test-integration - Tests d'intégration"
	@echo "  test-e2e      - Tests end-to-end"
	@echo ""
	@echo "🎨 Formatage:"
	@echo "  format        - Formater le code"
	@echo "  format-check  - Vérifier le formatage"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean         - Nettoyer les fichiers temporaires"
	@echo "  install       - Installer les dépendances"
	@echo "  dev-setup     - Setup environnement de développement"
	@echo ""
	@echo "🔒 Sécurité:"
	@echo "  security-check - Vérification de sécurité"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build  - Construire les images"
	@echo "  docker-test   - Tester les conteneurs"
	@echo "  docker-clean  - Nettoyer Docker"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs-build    - Construire la documentation"
	@echo "  docs-serve    - Servir la documentation"
	@echo ""
	@echo "🔄 Versions:"
	@echo "  bump          - Mettre à jour la version"
	@echo "  patch/minor/major - Types de mise à jour"
	@echo ""
	@echo "🎯 Spécial:"
	@echo "  zeroia        - Vérification ZeroIA complète"
	@echo "  check-all     - Toutes les vérifications"
	@echo "  deploy-check  - Vérification pré-déploiement"
