.ONESHELL:

build: warn
	python manage.py build

watch: warn
	python manage.py watch

clean: warn
	python manage.py clean

serve:
	python manage.py serve

warn:
	echo 'Using makefile for this task is deprecated. Run manage.py directly.'

.PHONY: build watch clean serve warn
