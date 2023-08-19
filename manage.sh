#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
if [[ -n ${XTRACE-} ]]; then
	set -o xtrace
fi

USE_VENV=true

build() {
	# TODO: Find an unused port?
	local port=8000
	local old_pid
	local pid

	echo "System Time: $(date)"

	venv-activate-if-needed
	if [[ -f .env ]]; then
		set -a
		source .env
		set +a
	fi

	clean
	ENV=pdf pelican
	old_pid="$(ps -ef | awk '/python -m http\.server 8000/ {print $2}')"
	if [[ -n $old_pid ]]; then
		kill -9 "$old_pid"
	fi
	pushd output
	python -m http.server $port &
	pid=$!
	popd

	sleep 1
	local pdfs_path=content/root-static/pdfs
	mkdir -pv $pdfs_path
	wkhtmltopdf --user-style-sheet pdf.css --zoom 1.2 --enable-internal-links \
		http://localhost:$port/resume \
		$pdfs_path/shrikant-sharat-kandula-resume.pdf
	kill -9 $pid

	pelican --ignore-cache --fatal errors
}

ppdf() {
	venv-activate-if-needed
	python gen-pdf.py
}

venv-activate-if-needed() {
	if ! $USE_VENV; then
		return
	fi
	if [[ ! -d venv ]]; then
		python3 -m venv --prompt sharats.me venv
	fi
	source venv/bin/activate
	if [[ -n "${CI-}" ]]; then
		pip-sync
	else
		if [[ ! -f requirements.txt || requirements.in -nt requirements.txt ]]; then
			pip-compile requirements.in
		fi
		if [[ ! -f venv/deps-sentinel || requirements.txt -nt venv/deps-sentinel ]]; then
			pip install -r requirements.txt
			touch venv/deps-sentinel
		fi
	fi
}

if [[ -z ${1-} ]]; then
	serve
else
	"$@"
fi
