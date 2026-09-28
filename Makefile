SHELL := /bin/bash
.DEFAULT_GOAL := help

CLUSTER      := preview
KUBE_CONTEXT := k3d-$(CLUSTER)
K3D_CONFIG   := k3d/cluster.yaml
CHART        := charts/preview-app
DOMAIN       := preview.localhost
API_DIR      := apps/api
VENV         := apps/api/.venv/bin
E2E_DIR      := e2e

.PHONY: help cluster-up cluster-down preview preview-down preview-list preview-reap e2e e2e-install api-install test lint chart-lint check-context require-pr

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

cluster-up: ## Create the local k3d cluster
	k3d cluster create --config $(K3D_CONFIG)

cluster-down: ## Delete the local k3d cluster
	k3d cluster delete $(CLUSTER)

preview: check-context require-pr ## Build and deploy a preview into pr-<PR>
	./scripts/preview-deploy.sh $(PR)

preview-down: check-context require-pr ## Delete the pr-<PR> environment
	./scripts/preview-destroy.sh $(PR)

preview-list: check-context ## List live preview environments
	./scripts/preview-list.sh

preview-reap: check-context ## Delete environments whose pull request is closed
	./scripts/preview-list.sh --reap

e2e-install: ## Install Playwright and the chromium browser
	cd $(E2E_DIR) && npm ci && npx playwright install --with-deps chromium

e2e: require-pr ## Run Playwright against pr-<PR>
	cd $(E2E_DIR) && PR_NUMBER=$(PR) GIT_SHA=$$(git rev-parse --short HEAD) \
		PREVIEW_URL=http://pr-$(PR).$(DOMAIN):8080 npm test

api-install: ## Create the API virtualenv
	python3 -m venv $(API_DIR)/.venv
	$(VENV)/pip install --quiet --upgrade pip
	$(VENV)/pip install --quiet -r $(API_DIR)/requirements-dev.txt

test: ## Run the API unit tests
	cd $(API_DIR) && .venv/bin/python -m pytest -q

lint: ## Lint and format-check the API
	cd $(API_DIR) && .venv/bin/ruff check .
	cd $(API_DIR) && .venv/bin/ruff format --check .

chart-lint: ## Lint and render the Helm chart
	helm lint $(CHART) --set pr=1
	helm template preview $(CHART) --set pr=1 > /dev/null

require-pr:
	@if [ -z "$(PR)" ]; then echo "Set PR, for example: make $(MAKECMDGOALS) PR=42"; exit 1; fi

check-context:
	@ctx=$$(kubectl config current-context 2>/dev/null); \
	if [ "$$ctx" != "$(KUBE_CONTEXT)" ]; then \
		echo "Current kube context is '$$ctx', expected '$(KUBE_CONTEXT)'. Refusing to touch another cluster."; \
		exit 1; \
	fi
