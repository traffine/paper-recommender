SHELL := /bin/bash

# Variables definitions
# -----------------------------------------------------------------------------

ifeq ($(TIMEOUT),)
TIMEOUT := 60
endif

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: test lint format run up down clean

test:
	poetry run pytest tests -vv --show-capture=all

lint:
	pysen run lint

format:
	pysen run format

run:
	poetry run start

st:
	poetry run streamlit run server/st.py

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build
