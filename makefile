build: public
	hugo # --cleanDestinationDir removes the `.git` file.
	echo sharats.me > public/CNAME
	touch public/.nojekyll

public:
	git worktree prune
	git worktree add public gh-pages

serve:
	hugo --buildDrafts server --bind 0.0.0.0

.PHONY: build serve
