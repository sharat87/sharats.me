build: | public
	hugo --cleanDestinationDir

public:
	mkdir public

serve:
	hugo --buildDrafts server --bind 0.0.0.0

.PHONY: build serve
