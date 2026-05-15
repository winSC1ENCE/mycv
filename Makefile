.DEFAULT_GOAL := help

COMPOSE := docker compose

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start the dev stack (db, backend, frontend) with hot reload.
	$(COMPOSE) up --build

down: ## Stop the dev stack.
	$(COMPOSE) down

logs: ## Tail backend logs.
	$(COMPOSE) logs -f backend

migrate: ## Run Django migrations inside the running backend container.
	$(COMPOSE) exec backend uv run python manage.py migrate

seed: ## Reload the curated CV seed data.
	$(COMPOSE) exec backend uv run python manage.py load_cv_seed --flush

shell: ## Open a Django shell inside the running backend container.
	$(COMPOSE) exec backend uv run python manage.py shell

test-backend: ## Run backend tests with coverage.
	cd backend && uv run pytest

test-frontend: ## Run frontend unit tests.
	cd frontend && npm test

test: test-backend test-frontend ## Run all tests.

lint-backend: ## Lint backend (ruff + black --check + mypy + bandit).
	cd backend && uv run ruff check . && uv run black --check . && uv run mypy . && uv run bandit -q -c pyproject.toml -r apps config

lint-frontend: ## Lint frontend (eslint + prettier --check + vue-tsc).
	cd frontend && npm run lint && npx prettier --check "src/**/*.{ts,vue,css,json}" && npm run typecheck

lint: lint-backend lint-frontend ## Run all lint checks.

build-backend: ## Build the production backend image.
	docker build -t mycv-backend:latest ./backend --target runtime

build-frontend: ## Build the production frontend image.
	docker build -t mycv-frontend:latest ./frontend --target runtime

.PHONY: help up down logs migrate seed shell test test-backend test-frontend lint lint-backend lint-frontend build-backend build-frontend
