.PHONY: build
.PHONY: upload
.PHONY: check

.venv: requirements.txt
	python3 -m venv .venv # Create venv
	.venv/bin/pip install -r requirements.txt  # Install requirements

build: .venv pyproject.toml README.md src/mcmu/*
	.venv/bin/python3 -m build  # Build package

upload: .venv .pypirc dist/mcmu/*
	.venv/bin/python3 -m twine upload dist/* --config-file .pypirc

check: .venv src/mcmu/*
	.venv/bin/bandit src/mcmu/*  # Check code
