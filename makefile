build:
	npx eleventy


serve:
	DEV_MODE=1 npx eleventy --serve --port 3030


deps:
	npm install


outdated:
	npm outdated


.PHONY: build serve deps outdated
