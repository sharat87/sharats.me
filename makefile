serve:
	hugo --buildDrafts server --bind 0.0.0.0

build:
	hugo

gh-pages:
	git clone -b gh-pages . .tmp-gh-pages
	hugo --destination .tmp-gh-pages --cleanDestinationDir
	echo sharats.me > .tmp-gh-pages/CNAME
	touch .tmp-gh-pages/.nojekyll
	git -C .tmp-gh-pages add .
	git -C .tmp-gh-pages ci -m 'Auto build website.'
	git -C .tmp-gh-pages push origin gh-pages
	rm -rf .tmp-gh-pages

.PHONY: serve build gh-pages
