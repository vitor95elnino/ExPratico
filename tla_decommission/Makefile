.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

.PHONY: virtualenv
virtualenv: SHELL:=/bin/bash
virtualenv: ## Creates a new virtual environment
	@virtualenv -p python3.8 .venv
	@bash -c "source .venv/bin/activate"
	@echo "If you're creating the .venv for the 1st time and you're using pycharm, don't forget to configure python interpreter and sources locations (see docs)"
	@echo "OK"

.PHONY: virtualenv-clear
virtualenv-clear: ## Deletes the current virtual enviroment
	@rm -rf .venv
	@echo "If you create the .venv again and you're using pycharm, don't forget to configure python interpreter and sources locations (see docs)"
	@echo "OK"

.PHONY:
clear: ## Clears the existing build files
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf src/*.egg-info
	@find . -name "*pycache*" | xargs rm -rf
	@echo "OK"

.PHONY: dev-update
dev-update: virtualenv ## Updates the local environment dependencies
	@pip install -r requirements.txt  --ignore-installed

.PHONY: dev-build
dev-build: virtualenv ## Prepares the local environment
	@pip install -r dev_requirements.txt
	@pre-commit install

.PHONY: install
install: ## Install all requirements and project
	@pip install -r requirements.txt
	@pip install .

.PHONY: test
test: dev-build ## Run the tests
	@pip install -e .
	@python tests_generator.py
	@python -W ignore::DeprecationWarning -m pytest tests/ --log-cli-level=DEBUG
#	python -m pytest tests/ --log-cli-level=DEBUG

.PHONY: test-coverage
test-coverage: dev-build ## Generates the coverage reports
	@pip install -e . --ignore-installed
	@coverage erase
	-coverage run -m pytest . --ignore=./var
	-coverage report -m
	-rm -rf htmlcov
	-coverage html
	@open htmlcov/index.html
