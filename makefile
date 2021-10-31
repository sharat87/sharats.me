PELICAN?=venv/bin/pelican
PELICANOPTS=


DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += --debug
endif

PORT ?= 0
ifneq ($(PORT), 0)
	PELICANOPTS += -p $(PORT)
endif


help:
	@echo 'make build -- to generate static assets'
	@echo 'make clean -- to delete generated assets'
	@echo 'make serve [PORT=8000] -- watch and server generated website'
	@echo 'make deploy -- build and deploy to GitHub Pages'

build: venv/deps-sentinel
	"$(PELICAN)" $(PELICANOPTS)

netlify:
	pelican $(PELICANOPTS)

clean:
	if test -d output; then rm -rf output; fi

serve: venv/deps-sentinel
	ENV=dev "$(PELICAN)" --listen --autoreload $(PELICANOPTS)

deploy: clean build
	ghp-import --message="Rebuild site" --branch=gh-pages output
	git push origin gh-pages

venv/deps-sentinel: requirements.txt
	source venv/bin/activate && pip install -r requirements.txt


.PHONY: help build clean serve deploy
