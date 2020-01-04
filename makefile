.ONESHELL:

build: warn
	python manage.py build

watch: warn
	python manage.py watch

clean: warn
	mkdir -p output
	rm -rf output/*

serve: build warn
	cd output
	python -m http.server 8010

warn:
	echo 'Using makefile is deprecated. Run manage.py directly.'

.PHONY: build watch clean serve warn
