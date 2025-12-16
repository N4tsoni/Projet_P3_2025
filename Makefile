.PHONY: help build up down restart logs shell test format lint type-check clean

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build les images Docker
	docker compose build

up: ## Lancer tous les services
	docker compose up -d

down: ## Arrêter tous les services
	docker compose down

restart: ## Redémarrer tous les services
	docker compose restart

logs: ## Voir les logs de tous les services
	docker compose logs -f

logs-backend: ## Voir les logs du backend
	docker compose logs -f backend

logs-frontend: ## Voir les logs du frontend
	docker compose logs -f frontend

logs-neo4j: ## Voir les logs de Neo4j
	docker compose logs -f neo4j

shell-backend: ## Accéder au shell du container backend
	docker compose exec backend bash

shell-frontend: ## Accéder au shell du container frontend
	docker compose exec frontend sh

test: ## Exécuter les tests
	docker compose exec backend poetry run pytest

test-cov: ## Exécuter les tests avec couverture
	docker compose exec backend poetry run pytest --cov=src --cov-report=html

test-connection: ## Tester la connexion à Neo4j et Graphiti
	docker compose exec backend poetry run python src/graph/test_connection.py

format: ## Formater le code avec Black
	docker compose exec backend poetry run black src/ tests/

lint: ## Vérifier le code avec Ruff
	docker compose exec backend poetry run ruff check src/ tests/

lint-fix: ## Corriger automatiquement les problèmes Ruff
	docker compose exec backend poetry run ruff check --fix src/ tests/

type-check: ## Vérifier les types avec MyPy
	docker compose exec backend poetry run mypy src/

quality: format lint type-check ## Vérifier la qualité du code (format, lint, types)

add: ## Ajouter une dépendance backend (usage: make add PACKAGE=nom-du-package)
	docker compose exec backend poetry add $(PACKAGE)

add-dev: ## Ajouter une dépendance de dev backend (usage: make add-dev PACKAGE=nom-du-package)
	docker compose exec backend poetry add --group dev $(PACKAGE)

add-frontend: ## Ajouter une dépendance frontend (usage: make add-frontend PACKAGE=nom-du-package)
	docker compose exec frontend npm install $(PACKAGE)

clean: ## Nettoyer les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

clean-docker: ## Nettoyer les volumes Docker (⚠️ perte de données)
	docker compose down -v

reset: clean-docker build up ## Reset complet du projet

neo4j: ## Ouvrir Neo4j Browser
	@echo "Ouvrir http://localhost:7474 dans votre navigateur"
	@echo "User: neo4j"
	@echo "Password: voir .env (défaut: graphrag2024)"

install-local: ## Installer les dépendances localement avec Poetry
	poetry install

update: ## Mettre à jour les dépendances backend
	docker compose exec backend poetry update

lock: ## Mettre à jour poetry.lock
	docker compose exec backend poetry lock

update-frontend: ## Mettre à jour les dépendances frontend
	docker compose exec frontend npm update
