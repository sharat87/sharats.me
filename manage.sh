#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
if [[ -n ${XTRACE:-} ]]; then
	set -o xtrace
fi

serve() {
	ensure-venv
	if [[ -f .env ]]; then
		set -a
		source .env
		set +a
	fi
	source venv/bin/activate
	export ENV=dev
	exec pelican --debug --listen --autoreload --port "${PORT:-8000}" --bind 0.0.0.0
}

build() {
	ensure-venv
	if [[ -f .env ]]; then
		set -a
		source .env
		set +a
	fi
	source venv/bin/activate
	pelican
	build-pdfs
}

netlify() {
	pelican
	build-pdfs
}

build-pdfs() {
	pushd output
	local port=8000
	../venv/bin/python -m http.server $port &
	pid=$!
	sleep 2
	wkhtmltopdf --user-style-sheet pdf.css --zoom 1.2 http://localhost:$port/resume static/shrikant-sharat-kandula-resume.pdf
	kill -9 $pid
	popd
}

clean() {
	rm -rf output
}

new-post() {
	local title
	read -rp "Title: " title
	local f
	f="content/posts/$(date +%Y-%m-%d)-$(
		echo "$title" \
			| tr '[:upper:]' '[:lower:]' \
			| sed -E -e s/\'//g -e 's/[^a-z0-9]+/-/g' -e 's/^-|-$//g'
	).md"
	if test -f "$f"; then
		echo File "'$f'" already exists. Exiting.
		return 1
	fi
	echo "Creating '$f'."
	printf "---\ntitle: %s\nstatus: draft\n---\n\nA brand new article here!" "$title" > "$f"
}

ensure-venv() {
	if [[ -f venv/deps-sentinel && requirements.txt -ot venv/deps-sentinel ]]; then
		return
	fi
	if [[ ! -d venv ]]; then
		python3 -m venv --prompt sharats.me venv
	fi
	(source venv/bin/activate; pip install -r requirements.txt)
	touch venv/make_sentinel
}

if [[ -z ${1-} ]]; then
	serve
else
	"$@"
fi
