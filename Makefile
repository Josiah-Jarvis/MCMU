.PHONY: build
build: src/mcmu/__main__.py
	python3 -m build

upload: dist/mcmu*
	python3 -m twine upload dist/mcmu*
