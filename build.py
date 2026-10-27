#!/usr/bin/env python3
"""Tiny static site builder for sharats.me. Replaces Pelican.

Usage:
    python build.py            # production build into output/
    python build.py --dev      # dev build (root-relative URLs, drafts listed)
    python build.py --serve    # dev build + watch + serve on :6060
"""
from __future__ import annotations

import argparse
import functools
import html
import http.server
import itertools
import re
import shutil
import sys
import threading
import traceback
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import markdown
from feedgenerator import Atom1Feed
from jinja2 import Environment, FileSystemLoader

import markdown_ext

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
THEME_DIR = ROOT / "theme"
OUTPUT_DIR = ROOT / "output"

AUTHOR = "Shrikant Sharat Kandula"
SITENAME = "The Sharat's"
PROD_SITEURL = "https://sharats.me"
FEED_PATH = "posts/index.xml"
TIMEZONE = timezone(timedelta(hours=5, minutes=30))  # Asia/Kolkata
SUMMARY_MAX_WORDS = 50

# Cloudflare Web Analytics site token (dashboard → Analytics & Logs → Web Analytics).
# The beacon is left out of dev builds, and entirely when this is empty.
CF_ANALYTICS_TOKEN = "2a3b6670f035477c9c2d803b95926618"

MENUITEMS = [
    ("Posts", "/posts/"),
    ("Labs", "/labs/"),
]

FILENAME_RE = re.compile(r"(?:(\d{4}-\d{2}-\d{2})-)?([-a-z0-9]*)")

# --- Markdown setup ----------------------------------------------------------

MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite",
        "markdown.extensions.extra",
        "markdown.extensions.toc",
        "markdown.extensions.sane_lists",
        "markdown.extensions.smarty",
        "markdown_ext",
    ],
    extension_configs={
        "markdown.extensions.codehilite": {
            "pygments_formatter": markdown_ext.CustomFormatter,
            "guess_lang": False,
            "cssclass": "hl",
        },
        "markdown.extensions.toc": {
            "title": "Table of Contents",
            "marker": "[TOC]",
            "permalink": True,
        },
    },
    output_format="html5",
)


def render_markdown(text: str) -> str:
    # Reset the collapsible-code-block counter so IDs are deterministic per
    # document, independent of build order.
    markdown_ext.CustomFormatter.collapse_counter = itertools.count()
    return MD.reset().convert(text)


def render_inline_markdown(text: str) -> str:
    """Jinja filter: render markdown and strip the wrapping <p></p>."""
    return markdown.markdown(text).strip()[len("<p>"):-len("</p>")]


def striptags(html_text: str) -> str:
    text = re.sub(r"<!--.*?-->|<[^>]*>", "", html_text, flags=re.S)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# --- Content parsing ---------------------------------------------------------


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse `---` fenced `key: value` front matter. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip()
    return meta, text[end + 4:].lstrip("\n")


def truncate_html_words(html_text: str, limit: int, end_text: str = " …") -> str:
    """Truncate HTML to `limit` words, closing any tags left open."""
    if limit <= 0:
        return ""
    SINGLETS = {"br", "col", "link", "base", "img", "param", "area", "hr", "input"}
    re_token = re.compile(r"&.*?;|<.*?>|(\w[\w-]*)", re.U)
    re_tag = re.compile(r"<(/)?(\w[\w-]*)(?:\s[^>]*)?(/?)>")
    words = 0
    pos = 0
    end_pos = None
    open_tags = []
    while words <= limit:
        m = re_token.search(html_text, pos)
        if not m:
            break
        pos = m.end()
        if m.group(1):  # a word
            words += 1
            if words == limit:
                end_pos = pos
            continue
        if end_pos is not None:
            continue
        tm = re_tag.match(m.group(0))
        if not tm:
            continue
        closing, name, self_closing = tm.group(1), tm.group(2).lower(), tm.group(3)
        if name in SINGLETS or self_closing:
            continue
        if closing:
            if name in open_tags:
                open_tags.remove(name)
        else:
            open_tags.insert(0, name)
    if end_pos is None:
        return html_text
    return html_text[:end_pos] + end_text + "".join(f"</{t}>" for t in open_tags)


class Content:
    def __init__(self, path: Path, kind: str, siteurl: str):
        self.kind = kind  # "article" or "page"
        self.path = path
        meta, body = parse_front_matter(path.read_text())

        name = path.stem
        date_str, slug = FILENAME_RE.fullmatch(name).groups()
        self.slug = slug

        self.title = meta.get("title", "")
        self.lang = "en"
        self.status = meta.get("status", "published")
        self.description = meta.get("description")
        self.hn_id = meta.get("hn_id")
        self.reddit_url = meta.get("reddit_url")
        date_str = meta.get("date", date_str)
        self.date = (
            datetime.combine(date.fromisoformat(date_str), time.min, TIMEZONE)
            if date_str
            else None
        )

        if kind == "article":
            if self.date and self.date > datetime.now(TIMEZONE) and "status" not in meta:
                # WITH_FUTURE_DATES = False
                self.status = "draft"
            self.url = f"posts/{self.slug}/"
            self.save_as = f"posts/{self.slug}/index.html"
            if self.status == "draft":
                self.url = f"drafts/{self.slug}.html"
                self.save_as = self.url
        else:
            self.url = f"{self.slug}/"
            self.save_as = meta.get("save_as", f"{self.slug}/index.html")

        self.content = render_markdown(body).replace("{static}", siteurl)
        self.summary = truncate_html_words(self.content, SUMMARY_MAX_WORDS)

    @property
    def locale_date(self):
        return self.date.strftime("%-d %b %Y") if self.date else ""


# --- The build ---------------------------------------------------------------


class Builder:
    def __init__(self, dev: bool):
        self.dev = dev
        self.siteurl = "" if dev else PROD_SITEURL

        self.jinja = Environment(
            loader=FileSystemLoader(THEME_DIR / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.jinja.filters["markdown"] = render_inline_markdown
        self.jinja.filters["striptags"] = striptags
        self.jinja.globals.update(
            SITENAME=SITENAME,
            SITEURL=self.siteurl,
            PROD_SITEURL=PROD_SITEURL,
            AUTHOR=AUTHOR,
            MENUITEMS=MENUITEMS,
            FEED_ALL_ATOM=FEED_PATH,
            FEED_DOMAIN=PROD_SITEURL,
            DEFAULT_LANG="en",
            THEME_STATIC_DIR="theme",
            ARCHIVES_URL="posts/",
            IS_DEV=dev,
            CF_ANALYTICS_TOKEN="" if dev else CF_ANALYTICS_TOKEN,
            current_year=date.today().strftime("%Y"),
            date_iso=date.today().isoformat(),
        )

        self.articles = []
        self.drafts = []
        self.pages = []
        self.now = datetime.now(TIMEZONE)

    def load_content(self):
        for path in sorted(CONTENT_DIR.glob("posts/*.md")):
            article = Content(path, "article", self.siteurl)
            (self.drafts if article.status == "draft" else self.articles).append(article)
        for path in sorted(CONTENT_DIR.glob("pages/**/*.md")):
            self.pages.append(Content(path, "page", self.siteurl))
        self.articles.sort(key=lambda a: a.date, reverse=True)
        self.drafts.sort(key=lambda a: a.date, reverse=True)

    def render(self, template_name: str, save_as: str, **context):
        template = self.jinja.get_template(template_name)
        context.setdefault("articles", self.articles)
        context.setdefault("drafts", self.drafts)
        context.setdefault("articles_page", SimpleNamespace(object_list=self.articles))
        context.setdefault("output_file", save_as)
        html_out = template.render(**context)
        out_path = OUTPUT_DIR / save_as
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out)

    def copy_static(self):
        for src, dest in [
            (CONTENT_DIR / "static", OUTPUT_DIR / "static"),
            (CONTENT_DIR / "root-static", OUTPUT_DIR),
            (THEME_DIR / "static", OUTPUT_DIR / "theme"),
        ]:
            if src.is_dir():
                shutil.copytree(
                    src,
                    dest,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".DS_Store"),
                )

    def write_feed(self):
        feed = Atom1Feed(
            title=SITENAME,
            link=PROD_SITEURL + "/",
            feed_url=f"{PROD_SITEURL}/{FEED_PATH}",
            description=None,
        )
        for article in self.articles:
            feed.add_item(
                # Titles may contain HTML entities (e.g. &mdash;); the feed
                # wants plain text, matching what Pelican produced.
                title=html.unescape(article.title),
                link=f"{PROD_SITEURL}/{article.url}",
                unique_id=f"tag:sharats.me,{article.date:%Y-%m-%d}:/{article.url}",
                author_name=AUTHOR,
                pubdate=article.date,
                updateddate=article.date,
                description=article.summary,
                content=article.content,
                categories=("posts",),
            )
        out_path = OUTPUT_DIR / FEED_PATH
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(feed.writeString("utf-8"))

    def write_sitemap(self):
        entries = []  # (url, lastmod, changefreq)
        entries.append(("/", self.now, "daily"))
        for page in self.pages:
            entries.append(("/" + page.url, self.now, "monthly"))
        for article in self.articles:
            entries.append(("/" + article.url, article.date, "monthly"))

        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 '
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"',
            'xmlns:xhtml="http://www.w3.org/1999/xhtml"',
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            "",
        ]
        for url, lastmod, changefreq in entries:
            lines += [
                "<url>",
                f"<loc>{PROD_SITEURL}{url}</loc>",
                f"<lastmod>{lastmod.isoformat(timespec='seconds')}</lastmod>",
                f"<changefreq>{changefreq}</changefreq>",
                "<priority>0.5</priority>",
                "</url>",
                "",
            ]
        lines.append("</urlset>")
        (OUTPUT_DIR / "sitemap.xml").write_text("\n".join(lines))

    def append_draft_redirects(self):
        """Old draft URLs 301 to their published location (for shared preview links)."""
        redirects = OUTPUT_DIR / "_redirects"
        with redirects.open("a") as f:
            for article in sorted(self.articles, key=lambda a: a.slug):
                f.write(f"/drafts/{article.slug}.html /posts/{article.slug} 301\n")

    def build(self):
        if OUTPUT_DIR.is_dir():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir()

        self.load_content()

        for article in self.articles + self.drafts:
            self.render("article.html", article.save_as, article=article)
        for page in self.pages:
            self.render("page.html", page.save_as, page=page)

        self.render("index.html", "index.html")
        self.render("archives.html", "posts/index.html")

        self.copy_static()
        self.write_feed()
        self.write_sitemap()
        if not self.dev:
            self.append_draft_redirects()

        print(
            f"Done: {len(self.articles)} articles, {len(self.drafts)} drafts, "
            f"{len(self.pages)} pages ({'dev' if self.dev else 'production'} build)."
        )


def serve(port: int):
    import watchfiles

    def rebuild():
        try:
            Builder(dev=True).build()
        except Exception:
            traceback.print_exc()

    rebuild()

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(OUTPUT_DIR)
    )
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Serving on http://127.0.0.1:{port} (watching for changes)")

    watch_targets = [CONTENT_DIR, THEME_DIR, ROOT / "markdown_ext.py"]
    for _changes in watchfiles.watch(*watch_targets):
        rebuild()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", action="store_true", help="development build")
    parser.add_argument("--serve", action="store_true", help="dev build + watch + serve")
    parser.add_argument("--port", type=int, default=6060)
    args = parser.parse_args()

    if args.serve:
        serve(args.port)
    else:
        Builder(dev=args.dev).build()


if __name__ == "__main__":
    sys.exit(main())
