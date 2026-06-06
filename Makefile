# ITERUN Makefile
# Usage: make <target>

.PHONY: help install install-dev install-ai setup run web shell test test-shell test-web test-ai \
        lint format clean docker-clean ollama-start ollama-pull env plan execute

# Default target
.DEFAULT_GOAL := help

# Load .env if exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variables with defaults
PYTHON ?= python
PIP ?= pip
PORT ?= 8080
HOST ?= 0.0.0.0
DEFAULT_MODEL ?= llama3.2
CONTAINER_PORT ?= 8000
CONTAINER_PREFIX ?= intent

# Colors
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

#------------------------------------------------------------------------------
# HELP
#------------------------------------------------------------------------------

help: ## Show this help
	@echo ""
	@echo "$(CYAN)ITERUN$(RESET) - DSL-based intent execution system"
	@echo ""
	@echo "$(GREEN)Usage:$(RESET) make <target>"
	@echo ""
	@echo "$(YELLOW)Setup:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^(install|setup|env)[^:]*:.*##/ {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Run:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^(run|web|shell|plan|execute|run-intent)[^:]*:.*##/ {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Test:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^test[^:]*:.*##/ {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)AI/Ollama:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^ollama[^:]*:.*##/ {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Maintenance:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^(clean|lint|format|docker)[^:]*:.*##/ {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

#------------------------------------------------------------------------------
# SETUP
#------------------------------------------------------------------------------

install: ## Install base dependencies
	$(PIP) install -r requirements.txt

install-dev: install ## Install development dependencies
	$(PIP) install pytest pytest-asyncio httpx anyio

install-ai: ## Install AI Gateway dependencies (LiteLLM)
	$(PIP) install litellm

setup: install install-ai env ## Full setup (install + AI + .env)
	@echo "$(GREEN)✓ Setup complete$(RESET)"

env: ## Create .env from .env.example if not exists
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env from .env.example$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ .env already exists$(RESET)"; \
	fi

#------------------------------------------------------------------------------
# RUN
#------------------------------------------------------------------------------

run: web ## Run web server (alias for 'web')

web: ## Start web server
	@echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)"
	$(PYTHON) -m web.app

shell: ## Start interactive shell
	@echo "$(CYAN)Starting interactive shell$(RESET)"
	$(PYTHON) -m cli.main

plan: ## Run dry-run on examples/01-user-api/intent.yaml
	$(PYTHON) -m cli.main plan examples/01-user-api/intent.yaml

execute: ## Execute examples/01-user-api/intent.yaml
	$(PYTHON) -m cli.main execute examples/01-user-api/intent.yaml

examples: ## Run all examples (dry-run)
	./examples/run-all.sh

# Run with custom intent file: make run-intent FILE=path/to/intent.yaml
run-intent: ## Run specific intent file (FILE=path/to/intent.yaml)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)ERROR: FILE not specified$(RESET)"; \
		echo "Usage: make run-intent FILE=path/to/intent.yaml"; \
		exit 1; \
	fi
	$(PYTHON) -m cli.main execute $(FILE)

#------------------------------------------------------------------------------
# TEST
#------------------------------------------------------------------------------

test: ## Run all tests
	$(PYTHON) -m pytest tests/ -v

test-shell: ## Run shell tests
	$(PYTHON) -m pytest tests/e2e/test_shell.py -v

test-web: ## Run web tests
	$(PYTHON) -m pytest tests/e2e/test_web.py -v

test-ai: ## Run AI Gateway tests
	$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

#------------------------------------------------------------------------------
# AI / OLLAMA
#------------------------------------------------------------------------------

ollama-start: ## Start Ollama server
	@echo "$(CYAN)Starting Ollama server...$(RESET)"
	ollama serve &
	@sleep 2
	@echo "$(GREEN)✓ Ollama server started$(RESET)"

ollama-pull: ## Pull default model (llama3.2)
	@echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)"
	ollama pull $(DEFAULT_MODEL)
	@echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)"

ollama-models: ## List recommended models
	@echo ""
	@echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)"
	@echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast"
	@echo "  llama3.2:1b    - 1B  - Ultra lightweight"
	@echo "  llama3.1:8b    - 8B  - Balanced"
	@echo "  mistral        - 7B  - Fast inference"
	@echo "  mistral-nemo   - 12B - Best quality"
	@echo "  gemma2         - 9B  - Google Gemma 2"
	@echo "  phi3           - 3.8B - Microsoft Phi-3"
	@echo "  qwen2.5        - 7B  - Alibaba Qwen"
	@echo "  codellama      - 7B  - Code generation"
	@echo ""
	@echo "$(YELLOW)Install:$(RESET) ollama pull <model>"
	@echo ""

ollama-status: ## Check Ollama status
	@echo "$(CYAN)Checking Ollama status...$(RESET)"
	@curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \
		echo "$(GREEN)✓ Ollama is running$(RESET)" || \
		echo "$(RED)✗ Ollama is not running$(RESET)"

#------------------------------------------------------------------------------
# MAINTENANCE
#------------------------------------------------------------------------------

lint: ## Run linting (if ruff installed)
	@which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)"

format: ## Format code (if ruff installed)
	@which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)"

clean: ## Clean cache and temp files
	@echo "$(CYAN)Cleaning...$(RESET)"
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache */.pytest_cache
	rm -rf *.egg-info .eggs
	rm -rf htmlcov .coverage
	rm -rf /tmp/intent-*
	@echo "$(GREEN)✓ Cleaned$(RESET)"

docker-clean: ## Remove all intent-* containers and images
	@echo "$(CYAN)Cleaning Docker resources...$(RESET)"
	-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f
	-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f
	@echo "$(GREEN)✓ Docker cleaned$(RESET)"

docker-ps: ## List running intent containers
	@docker ps --filter "name=$(CONTAINER_PREFIX)-"

docker-stop: ## Stop all intent containers
	@docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop
	@echo "$(GREEN)✓ Containers stopped$(RESET)"

#------------------------------------------------------------------------------
# DEVELOPMENT
#------------------------------------------------------------------------------

dev: ## Run web server with auto-reload (requires uvicorn[standard])
	uvicorn web.app:app --reload --host $(HOST) --port $(PORT)

new-intent: ## Create new intent interactively
	$(PYTHON) -m cli.main new

show-config: ## Show current configuration
	@echo ""
	@echo "$(CYAN)Current Configuration:$(RESET)"
	@echo "  HOST=$(HOST)"
	@echo "  PORT=$(PORT)"
	@echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)"
	@echo "  CONTAINER_PORT=$(CONTAINER_PORT)"
	@echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)"
	@echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)"
	@echo "  SKIP_AMEN_CONFIRMATION=$(SKIP_AMEN_CONFIRMATION)"
	@echo ""
