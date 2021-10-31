import os, os.path
from glob import glob

from pygments.formatters import HtmlFormatter

is_dev = os.getenv("ENV") == "dev"

AUTHOR = "Shrikant Sharat Kandula"
SITENAME = "The Sharat's"
SITEURL = "" if is_dev else "https://sharats.me"

THEME = "theme"

PATH = "content"

_root_static = "root-static"
STATIC_PATHS = ["static", _root_static]

EXTRA_PATH_METADATA = {
    os.path.relpath(filename, start=PATH): { "path": os.path.basename(filename) }
    for filename in glob(os.path.join(PATH, _root_static, "*"))
}

class HtmlFlexFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield 0, '<code>'
        for i, t in source:
            if i == 1:
                # it's a line of formatted code
                t += '<br>'
            yield i, t
        yield 0, '</code>'


codehilite_plugin = "markdown.extensions.codehilite"
# codehilite_plugin = "codehilite_ssk"
MARKDOWN = {
    # Extensions at <https://python-markdown.github.io/extensions/>.
    "extension_configs": {
        codehilite_plugin: {
            "guess_lang": False,
            "cssclass": "hl",
            "pygments_formatter": HtmlFlexFormatter,
        },
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
        "markdown.extensions.toc": {
            "marker": "[TOC]",
        },
        "markdown_ext": {},
    },
    "output_format": "html5",
}

TIMEZONE = "Asia/Kolkata"

DEFAULT_LANG = "en"

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = "posts/index.xml"

DELETE_OUTPUT_DIRECTORY = True

# Content with dates in the future should get a default status of `draft`.
WITH_FUTURE_DATES = False

# Order is hard to get if pages were to show automatically in the menu.
DISPLAY_PAGES_ON_MENU = False
MENUITEMS = [
    ("Posts", "/posts/"),
    ("Labs", "/labs/"),
    ("About", "/about/"),
    ("Contact", "/contact/"),
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
#GOOGLE_ANALYTICS = ""

PLUGINS = [
    "sitemap",
]

SITEMAP = {
    "format": "xml",
}
