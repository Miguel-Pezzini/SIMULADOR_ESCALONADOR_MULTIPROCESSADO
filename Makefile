PYTHON ?= python3

.PHONY: test qualidade experimentos

test:
	$(PYTHON) -m pytest

qualidade:
	$(PYTHON) -m ruff check src testes experimentos
	$(PYTHON) -m ruff format --check src testes experimentos
	$(PYTHON) -m mypy src
	$(PYTHON) -m pytest --cov=simulador --cov-report=term-missing --cov-fail-under=85

experimentos:
	$(PYTHON) experimentos/rodar.py
	$(PYTHON) experimentos/graficos.py
