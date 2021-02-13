build: node_modules
	npx eleventy


serve:
	DEV_MODE=1 npx eleventy --serve --port 3030


node_modules: node_modules/make_sentinel


node_modules/make_sentinel: package.json
	npm install


outdated:
	npm outdated


.PHONY: build serve deps outdated
