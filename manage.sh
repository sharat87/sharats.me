#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
if [[ -n ${XTRACE-} ]]; then
	set -o xtrace
fi

USE_VENV=true

serve() {
	venv-activate-if-needed
	if [[ -f .env ]]; then
		set -a
		source .env
		set +a
	fi
	export ENV=dev
	exec python -m pelican --debug --listen --autoreload --port "${PORT:-8000}" --bind 0.0.0.0
}

build() {
	local port=8000
	local pid

	venv-activate-if-needed
	if [[ -f .env ]]; then
		set -a
		source .env
		set +a
	fi

	# TODO: Find an unused port?
	export ENV=pdf
	python -m pelican --debug --listen --port $port --bind 0.0.0.0 &
	pid=$!
	sleep 3
	wkhtmltopdf --user-style-sheet pdf.css --zoom 1.2 --enable-internal-links \
		http://localhost:$port/resume \
		output/static/shrikant-sharat-kandula-resume.pdf
	kill -9 $pid

	pelican --debug --ignore-cache --fatal errors
}

netlify() {
	USE_VENV=false
	build
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

venv-activate-if-needed() {
	if ! $USE_VENV; then
		return
	fi
	if [[ ! -d venv ]]; then
		python3 -m venv --prompt sharats.me venv
	fi
	source venv/bin/activate
	if [[ -f venv/deps-sentinel && requirements.txt -ot venv/deps-sentinel ]]; then
		pip install -r requirements.txt
		touch venv/deps-sentinel
	fi
}

if [[ -z ${1-} ]]; then
	serve
else
	"$@"
fi
