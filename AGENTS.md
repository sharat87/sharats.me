# AGENTS.md

Source of [sharats.me](https://sharats.me), a personal blog. Static site built
by `build.py`, a small custom builder (~400 lines, replaced Pelican in 2026).
Content in Markdown.

## Stack

- Python 3.13 (see `.python-version` / `.tool-versions`), managed with **uv**
  (`pyproject.toml` + `uv.lock`). Deps: `markdown`, `jinja2`, `pygments`,
  `feedgenerator`, `watchfiles`. No framework.
- [Task](https://taskfile.dev) (`Taskfile.dist.yml`) is the task runner.
- Served by a Cloudflare Worker (static assets only, config in
  `wrangler.jsonc`). Workers Builds deploys on push to `master`: it runs
  `ci-build.sh` (installs uv, `uv sync --no-dev`, runs `build.py`), then
  `npx wrangler deploy`. Build settings live in the Cloudflare dashboard. DNS
  for sharats.me (proxied records, www to apex redirect) is in
  `~/labs/infra/dns`.
- Analytics: Cloudflare Web Analytics beacon in `base.html`, production builds
  only (`CF_ANALYTICS_TOKEN` in `build.py`).

## Commands

```sh
task serve   # background dev server on http://127.0.0.1:6060 (via serve.sh)
task build   # production build into output/
task new -- "Post Title"   # scaffold a new draft in content/posts/
```

Or directly: `uv run python build.py [--dev | --serve] [--port N]`.

`serve.sh` runs the dev server (rebuild-on-change + serve) in a background
tmux window (socket `daemons`, window `sharats-me-dev`), logging to
`.logs/dev-server.log`. Re-running it restarts the server. To stop it:
`tmux -L daemons kill-window -t sharats-me-dev`.

## Layout

- `build.py` — the whole build: front matter parsing, Markdown rendering,
  Jinja templating, Atom feed, sitemap, static copying, draft redirects, dev
  server. All site config (author, URLs, menu) is constants at the top.
- `content/posts/YYYY-MM-DD-slug.md` — articles. Date/slug parsed from the
  filename; front matter is `---`-fenced `key: value` lines. `status: draft`
  keeps a post unpublished (drafts render under `/drafts/<slug>.html` and are
  excluded from listings, feed and sitemap). Future-dated posts are treated as
  drafts.
- `content/pages/` — standalone pages (labs, 404, licenses), rendered at
  `/{slug}/`.
- `content/root-static/` — files copied to the site root (favicons,
  `_redirects`, `_headers`, etc.).
- `content/static/` — other static assets, copied to `/static/`.
- `theme/` — custom Jinja2 theme (`templates/` + `static/`, the latter copied
  to `/theme/`).
- `markdown_ext.py` — custom Python-Markdown extensions (incl. a custom
  Pygments formatter with collapsible code blocks).

## Conventions & gotchas

- **Always commit when finished.** Never leave dangling uncommitted changes.
  Amend the previous commit for follow-up changes when asked.
- New posts: use `task new -- "Title"`, which scaffolds front matter with
  `status: draft` and a `[TOC]` marker.
- Articles are at `/posts/{slug}/`; the archive index is `/posts/`. There are
  no tag pages, author pages or translations — those concepts were removed;
  `tags:` lines in old front matter are simply ignored. Old `/tags/*` URLs
  301 to `/posts/`.
- Atom feed: `/posts/index.xml`. Legacy Pelican feed URLs (`/feeds/*`) 301 to
  it via `content/root-static/_redirects`.
- The production build appends 301 redirects from `/drafts/<slug>.html` to
  `/posts/<slug>` for every published post (`append_draft_redirects` in
  `build.py`).
- The build machine may need `UV_CACHE_DIR` set if `~/.cache/uv` is not
  writable.

## License

Content: CC BY-SA; code: MIT. All content © Shrikant Sharat Kandula.
