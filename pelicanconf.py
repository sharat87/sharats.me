import os, os.path
from glob import glob

is_dev = os.getenv("ENV") == "dev"

AUTHOR = "Shrikant Sharat Kandula"
SITENAME = "The Sharat's"
PROD_SITEURL = "https://sharats.me"
SITEURL = "http://localhost:8000" if is_dev else PROD_SITEURL

THEME = "theme"

PATH = "content"

_root_static = "root-static"
STATIC_PATHS = ["static", _root_static]

EXTRA_PATH_METADATA = {
    os.path.relpath(filename, start=PATH): { "path": os.path.basename(filename) }
    for filename in glob(os.path.join(PATH, _root_static, "*"))
}

FILENAME_METADATA = r"(?:(?P<date>\d{4}-\d{2}-\d{2})-)?(?P<slug>[-a-z0-9]*)"

MARKDOWN = {
    # Extensions at <https://python-markdown.github.io/extensions/>.
    "extension_configs": {
        "markdown.extensions.codehilite": {
            "guess_lang": False,
            "cssclass": "hl",
        },
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
        "markdown.extensions.toc": {
            "title": "Contents",
            "marker": "[TOC]",
            "permalink": True,
        },
        "markdown.extensions.sane_lists": {},
        "markdown.extensions.smarty": {},
        "markdown_ext": {},
    },
    "output_format": "html5",
}

TIMEZONE = "Asia/Kolkata"

FEED_DOMAIN = PROD_SITEURL
FEED_ALL_ATOM = "posts/index.xml"

DELETE_OUTPUT_DIRECTORY = True

# Content with dates in the future should get a default status of `draft`.
WITH_FUTURE_DATES = False

# Order is hard to get if pages were to show automatically in the menu. So we specify explicitly.
MENUITEMS = [
    ("Posts", "/posts/"),
    ("Labs", "/labs/"),
    # ("Rèsumè", "/resume/"),
    ("About", "/about/"),
]

SOCIAL = [
    ("GitHub", "/github"),
    ("LinkedIn", "/linkedin"),
    ("Twitter", "/twitter"),
]

DEFAULT_PAGINATION = False

RELATIVE_URLS = False

ARTICLE_URL = "posts/{slug}/"
ARTICLE_SAVE_AS = "posts/{slug}/index.html"

PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"

ARCHIVES_URL = "posts/"
ARCHIVES_SAVE_AS = "posts/index.html"

TAG_URL = "tags/{slug}/"
TAG_SAVE_AS = "tags/{slug}/index.html"

DATE_FORMATS = {
    "en": "%-d %b %Y",
}


def _render_markdown(text: str):
    from markdown import markdown
    return markdown(text).strip()[len("<p>"):-len("</p>")]


JINJA_FILTERS = {
    "markdown": _render_markdown,
}

DISQUS_SITENAME = "sharats-me"



PLUGINS = [
    "pelican_ext",
    "sitemap",
]

SITEMAP = {
    "format": "xml",
}
if is_dev:
    SITEMAP["exclude"] = ["drafts/"]
