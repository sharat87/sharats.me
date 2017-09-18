serve:
	hugo --buildDrafts server --bind 0.0.0.0

build:
	hugo

.PHONY: serve build
