# AGENTS.md

Source of [sharats.me](https://sharats.me), a personal blog. Static site built
with [Pelican](https://docs.getpelican.com/), content in Markdown.

## Stack

- Python 3.13 (see `.python-version` / `.tool-versions`), managed with **uv**
  (`pyproject.toml` + `uv.lock`).
- [Task](https://taskfile.dev) (`Taskfile.dist.yml`) is the task runner.
- Deployed on Netlify; the build command runs `netlify-ci.sh` (installs uv,
  `uv sync --no-dev`, runs pelican). There is no `netlify.toml`; deploy
  settings live in the Netlify UI.

## Commands

```sh
task serve   # dev server with autoreload on http://127.0.0.1:6060 (ENV=dev)
task build   # production build into output/ (also appends draft redirects to output/_redirects)
task new -- "Post Title"   # scaffold a new draft in content/posts/
```

Without Task, the equivalent of a build is:

```sh
uv sync
PYTHONPATH=. uv run pelican --ignore-cache --fatal errors
```

## Layout

- `content/posts/YYYY-MM-DD-slug.md` — articles. Filename date/slug are parsed
  via `FILENAME_METADATA` in `pelicanconf.py`. `status: draft` keeps a post
  unpublished (drafts render under `/drafts/`).
- `content/pages/` — standalone pages (resume, labs, 404, licenses).
- `content/root-static/` — files copied to the site root (favicons,
  `_redirects`, `_headers`, etc.) via `EXTRA_PATH_METADATA`.
- `content/static/` — other static assets.
- `theme/` — custom Jinja2 theme (`templates/` + `static/`).
- `pelicanconf.py` — all Pelican settings, including the Markdown extension
  config and URL scheme (`posts/{slug}/`).
- `markdown_ext.py` — custom Python-Markdown extensions (incl. a custom
  Pygments formatter). Registered as the `markdown_ext` extension.

## Conventions & gotchas

- **Always commit when finished.** Never leave dangling uncommitted changes.
  Amend the previous commit for follow-up changes when asked.
- New posts: use `task new -- "Title"`, which scaffolds front matter with
  `status: draft` and a `[TOC]` marker.
- Articles are at `/posts/{slug}/`; the archive index is `/posts/`.
- Atom feed: `/posts/index.xml`; sitemap via the `pelican-sitemap` plugin.
- `task build` appends 301 redirects from `/drafts/<slug>.html` to
  `/posts/<slug>` for every published post.
- `--fatal errors` is used in builds; keep builds warning-clean.
- The build machine may need `UV_CACHE_DIR` set if `~/.cache/uv` is not
  writable.

## License

Content: CC BY-SA; code: MIT. All content © Shrikant Sharat Kandula.
