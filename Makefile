.PHONY: help install install-dev test test-cov lint format type-check clean build upload upload-test check-all

help:
	@echo "Available commands:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run flake8 linter"
	@echo "  format        Format code with black"
	@echo "  type-check    Run mypy type checker"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  upload        Upload package to PyPI"
	@echo "  upload-test   Upload package to TestPyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=langchain_iointelligence --cov-report=html --cov-report=term

lint:
	flake8 langchain_iointelligence/ tests/ examples/

format:
	black langchain_iointelligence/ tests/ examples/

type-check:
	mypy langchain_iointelligence/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository testpypi dist/*

check-all: format lint type-check test-cov
	@echo "All checks passed!"
