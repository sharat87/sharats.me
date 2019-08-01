.ONESHELL:

build: clean
	python build.py

clean:
	rm -rf output

serve: build
	cd output; python -m http.server --port 8010

.PHONY: build serve
