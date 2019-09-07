.ONESHELL:

build:
	python build.py

clean:
	mkdir -p output
	rm -rf output/*

serve: build
	cd output
	python -m http.server 8010

.PHONY: build clean serve
