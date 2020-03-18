build:
	npx eleventy


serve:
	DEV_MODE=1 npx eleventy --serve --port 3030


deps:
	npm install


.PHONY: build serve deps
