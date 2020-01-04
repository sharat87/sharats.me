.ONESHELL:

build:
	python --version
	python manage.py build

clean:
	mkdir -p output
	rm -rf output/*

serve: build
	cd output
	python -m http.server 8010

.PHONY: default info build clean serve
