build:
	hugo --cleanDestinationDir

serve:
	hugo --buildDrafts server --bind 0.0.0.0

.PHONY: build serve
