#!/usr/bin/env python3
"""Tiny static site builder for sharats.me. Replaces Pelican.

Usage:
    python build.py            # production build into output/
    python build.py --dev      # dev build (root-relative URLs, drafts listed)
"""
from __future__ import annotations

import argparse
import html
import itertools
import re
import shutil
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape, quoteattr

import markdown

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
    """Render markdown and strip the wrapping <p></p>."""
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


# --- Templates ---------------------------------------------------------------
#
# Plain functions returning HTML. Nothing is escaped: titles, content and
# summaries are trusted HTML from our own Markdown. `site` is the Builder.


def truncate(text: str, length: int, end: str = "...", leeway: int = 5) -> str:
    """Cut at a word boundary, like Jinja's `truncate` filter did."""
    if len(text) <= length + leeway:
        return text
    return text[: length - len(end)].rsplit(" ", 1)[0] + end


def base(site, *, title: str, content: str, active: str = "", extra_head: str = "") -> str:
    """The page layout. `active` is the menu link to highlight."""
    nav = "".join(
        f'<a href="{link}"{" class=active" if link == active else ""}>{name}</a>'
        for name, link in MENUITEMS
    )
    beacon = (
        '<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js"'
        f""" data-cf-beacon='{{"token": "{CF_ANALYTICS_TOKEN}"}}'></script>"""
        if not site.dev and CF_ANALYTICS_TOKEN
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
	<meta charset=utf-8>
	<title>{title}{" — " if title else ""}{SITENAME}</title>
	<meta name=viewport content="width=device-width, initial-scale=1">
	<link rel=manifest href="/site.webmanifest">
	<link rel=apple-touch-icon href="/apple-touch-icon.png">
	<link rel=stylesheet href="{site.siteurl}/theme/styles.css">
	<style>.hide, .sr-only {{ display: none !important; }}</style>
	<link rel=alternate href="/posts/index.xml" type="application/atom+xml" title="{SITENAME}">
	{extra_head}
</head>

<body>

	<header>
		<div class=brand><a href="{site.siteurl}/" rel=home title="Go Home"><img src="/apple-touch-icon.png" alt="" width=28 height=28>{SITENAME}</a></div>
		<nav>{nav}<a href="{PROD_SITEURL}/{FEED_PATH}" title="Atom Feed">Feed</a></nav>
	</header>

	<main>{content}</main>

	<footer>
		© 2010&ndash;{site.now:%Y} Shrikant Sharat Kandula. Source on <a href="https://github.com/sharat87/sharats.me" target=_blank rel=noopener>GitHub</a>.
			Content licensed with <a href="/licenses/cc-by/">CC-BY</a>, and code with <a href="/licenses/mit/">MIT License</a>.
	</footer>

	<script src="{site.siteurl}/theme/main.js"></script>
	{beacon}
</body>
</html>
"""


def article_listing(site, articles) -> str:
    """A list of posts. Dev builds list drafts first."""
    if site.dev:
        articles = site.drafts + articles
    items = "".join(
        f"""
	<li>
		<small class=subtext>
			<time datetime='{a.date.isoformat()}'>{a.locale_date}</time>
		</small>
		<span class=title-wrap>
			<a href="{site.siteurl}/{a.url}" class=title>{render_inline_markdown(a.title)}</a>{" <span class=draft-badge>Draft</span>" if a.status == "draft" else ""}
		</span>"""
        for a in articles
    )
    return f"<ul class=post-list>{items}\n</ul>\n"


def article_page(site, article) -> str:
    extra_head = (
        f'<meta name=description content="{truncate(striptags(article.summary), 150)}">'
        if article.summary
        else ""
    )

    status = (
        f"\n\t&middot; <span class=draft-badge>{article.status}</span>"
        if article.status != "published"
        else ""
    )
    lede = (
        f"\n<p class=lede>{render_inline_markdown(article.description)}</p>"
        if article.description
        else ""
    )

    discuss_links = []
    if article.hn_id:
        discuss_links.append(
            f'<a target=_blank href="https://news.ycombinator.com/item?id={article.hn_id}">Hacker News</a>'
        )
    if article.reddit_url:
        discuss_links.append(
            f'<a target=_blank href="https://www.reddit.com/{article.reddit_url}">Reddit</a>'
        )
    discuss = (
        f"\n<p><b>Discuss on</b>: {' or '.join(discuss_links)}.</p>" if discuss_links else ""
    )

    content = f"""
<h1>{render_inline_markdown(article.title)}</h1>
<p class=post-meta>
	<time datetime="{article.date.isoformat()}">{article.locale_date}</time>{status}
</p>

<article>{lede}
{article.content}
</article>{discuss}"""

    return base(site, title=striptags(article.title), content=content, extra_head=extra_head)


def page_page(site, page) -> str:
    content = f"""
<section id="content" class="body">
    <h1 class="entry-title">{page.title}</h1>
    {page.content}
</section>
"""
    return base(site, title=page.title, content=content, active=f"/{page.url}")


def archives_page(site) -> str:
    content = f"""
<h1>Posts</h1>

{article_listing(site, site.articles)}
"""
    return base(site, title="Posts", content=content, active="/posts/")


def index_page(site) -> str:
    content = f"""
<h1>Namaste 🙏</h1>

<p>I am Shrikant. This is my blog/website where I write stuff about the work I do and things I've learnt.</p>

<h2>Recent Posts</h2>
{article_listing(site, site.articles[:6])}
<p><a href="{site.siteurl}/posts/">See all posts &rarr;</a></p>

<h2 id=labs>Labs</h2>

<h3>
	Httpbun <small><a href="https://httpbun.com/" target=httpbun rel=noopener>httpbun.com</a></small>
</h3>

<p>This is an HTTP service with endpoints that are useful when testing any HTTP client, like a browser, a library, or any API developer tool. It's heavily inspired by <a href="https://httpbin.org" rel=noopener>httpbin</a>.</p>

<h3>
	Just a calendar <small><a href="https://cal.sharats.me/" target="just-a-calendar" rel="noopener">cal.sharats.me</a></small>
</h3>

<p>An easily reachable endpoint to have a calendar to look at. No signup, no setup, no downloads, no flash and very little features. Perfect when you want to show a calendar and talk about dates when sharing your screen in a presentation or meeting.</p>

<p><a href="{site.siteurl}/labs/">See all &rarr;</a></p>
"""
    return base(site, title="", content=content)


# --- The build ---------------------------------------------------------------


class Builder:
    def __init__(self, dev: bool):
        self.dev = dev
        self.siteurl = "" if dev else PROD_SITEURL

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

    def write_html(self, save_as: str, html_out: str):
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
        def link(href, rel):
            return f"<link href={quoteattr(href)} rel={quoteattr(rel)}/>"

        parts = [
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<feed xmlns="http://www.w3.org/2005/Atom">',
            f"<title>{xml_escape(SITENAME)}</title>",
            link(PROD_SITEURL + "/", "alternate"),
            link(f"{PROD_SITEURL}/{FEED_PATH}", "self"),
            f"<id>{xml_escape(PROD_SITEURL)}/</id>",
            f"<updated>{max(a.date for a in self.articles).isoformat()}</updated>",
        ]
        for article in self.articles:
            url = f"{PROD_SITEURL}/{article.url}"
            parts += [
                "<entry>",
                # Titles may contain HTML entities (e.g. &mdash;); the feed
                # wants plain text, matching what Pelican produced.
                f"<title>{xml_escape(html.unescape(article.title))}</title>",
                link(url, "alternate"),
                f"<published>{article.date.isoformat()}</published>",
                f"<updated>{article.date.isoformat()}</updated>",
                f"<author><name>{xml_escape(AUTHOR)}</name></author>",
                f"<id>tag:sharats.me,{article.date:%Y-%m-%d}:/{xml_escape(article.url)}</id>",
                f'<summary type="html">{xml_escape(article.summary)}</summary>',
                f'<content type="html">{xml_escape(article.content)}</content>',
                '<category term="posts"/>',
                "</entry>",
            ]
        parts.append("</feed>")
        out_path = OUTPUT_DIR / FEED_PATH
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("".join(parts))

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
                f.write(f"/drafts/{article.slug}.html /posts/{article.slug}/ 301\n")

    def build(self):
        if OUTPUT_DIR.is_dir():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir()

        self.load_content()

        for article in self.articles + self.drafts:
            self.write_html(article.save_as, article_page(self, article))
        for page in self.pages:
            self.write_html(page.save_as, page_page(self, page))

        self.write_html("index.html", index_page(self))
        self.write_html("posts/index.html", archives_page(self))

        self.copy_static()
        self.write_feed()
        self.write_sitemap()
        if not self.dev:
            self.append_draft_redirects()

        print(
            f"Done: {len(self.articles)} articles, {len(self.drafts)} drafts, "
            f"{len(self.pages)} pages ({'dev' if self.dev else 'production'} build)."
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", action="store_true", help="development build")
    args = parser.parse_args()

    Builder(dev=args.dev).build()


if __name__ == "__main__":
    sys.exit(main())
