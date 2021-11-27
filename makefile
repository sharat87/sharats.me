serve: venv/deps-sentinel
	if [[ -f .env ]]; then set -a; source .env; set +a; fi; \
		source venv/bin/activate; \
		ENV=dev pelican --debug --listen --autoreload --port $${PORT:-8000} --bind 0.0.0.0

build: venv/deps-sentinel
	if [[ -f .env ]]; then set -a; source .env; set +a; fi; \
		source venv/bin/activate; \
		pelican

netlify:
	pelican

clean:
	rm -rf output

new-post:
	@read -p "Title: " title \
		&& f="content/posts/$$(date +%Y-%m-%d)-$$(echo "$$title" | tr A-Z a-z | sed -E -e 's/[^a-z0-9]+/-/g' -e 's/^-|-$$//g').md" \
		&& if test -f "$$f"; then echo File "'$$f'" already exists. Exiting.; exit 1; fi; \
		echo "Creating '$$f'." \
		&& echo "---\ntitle: $$title\nstatus: draft\n---\n\nA brand new article here!" > "$$f"

venv/deps-sentinel: requirements.txt
	source venv/bin/activate && pip install -r requirements.txt
	touch venv/deps-sentinel


.PHONY: serve build netlify clean new-post
