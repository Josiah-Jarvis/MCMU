.PHONY: build
.PHONY: upload
.PHONY: check

build: src/mcmu/
	python3 -m build

upload: dist/mcmu*
	python3 -m twine upload dist/* --config-file .pypirc

check: src/mcmu/*
	bandit src/mcmu/*
