"""
Build my blog site. No command line arguments. Just run `python build.py`.

For math support, checkout mistune_contrib's math mixin at
https://github.com/lepture/mistune-contrib/blob/master/mistune_contrib/math.py
"""

from collections import defaultdict
from pathlib import Path
import datetime as dt
import logging
import re
import shutil

import yaml
import jinja2
import mistune
from feedgen.feed import FeedGenerator
from mistune_contrib.highlight import HighlightMixin
from mistune_contrib.toc import TocMixin


class Config:
    site_url = 'https://www.sharats.me'
    site_title = "The Sharat's"
    author = 'Shrikant Sharat Kandula'
    email = 'shrikantsharat.k@gmail.com'


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

SCRIPT_LOC = Path(__file__).resolve()
ROOT_LOC = SCRIPT_LOC.parent
OUTPUT_DIR = ROOT_LOC / 'output'
CONTENT_DIR = ROOT_LOC / 'content'

env = jinja2.Environment(loader=jinja2.PackageLoader(__name__), autoescape=jinja2.select_autoescape(['html', 'xml']))

markdown = mistune.Markdown(renderer=type('Renderer', (TocMixin, HighlightMixin, mistune.Renderer), {})())
markdown.renderer.options.update(inlinestyles=False, linenos=False)


class Page:
    def __init__(self, path):
        self.path = path
        self.slug = path.stem
        self.meta = {}
        self.tags = set()
        self.date = None

        body = self.path.read_text()

        if body.startswith('---\n'):
            meta_block, body = body[4:].split('\n---\n', 1)
            self.meta = yaml.safe_load(meta_block)
            if 'tags' in self.meta:
                self.tags.update(self.meta.pop('tags'))

        self.body = body
        self.html_body = md_to_html(body)

        match = re.fullmatch(r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>[-\w]+)', self.slug)
        if match:
            self.date = dt.datetime.fromisoformat(match.group('date')).date()
            self.slug = match.group('slug')

    def title(self):
        return self.meta.get('title') or self.slug.title()

    def link(self):
        return f'/posts/{self.slug}.html'

    def permalink(self):
        return Config.site_url + self.link()

    def output_path(self):
        return self.path.relative_to(CONTENT_DIR).with_suffix('.html')

    def date_display(self):
        return self.date.strftime('%b %d, %Y') if self.date else ''

    def date_iso(self):
        return self.date.isoformat() if self.date else ''

    def should_publish(self):
        return self.meta.get('publish', True) and (self.date is None or self.date <= dt.date.today())

    def __str__(self):
        return f'<{self.__class__.__name__} {self.slug}>'

    __repr__ = __str__


def md_to_html(md_content: str):
    markdown.renderer.reset_toc()
    html = markdown(md_content)
    if markdown.renderer.toc_tree and '<!-- TOC -->' in html:
        html = html.replace('<!-- TOC -->', '<div class=toc>' + markdown.renderer.render_toc(level=3) + '</div>')
    return html


def render(target, template, **kwargs):
    markup = env.get_template(template).render(config=Config, **kwargs)
    dest = OUTPUT_DIR / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding='utf-8')


def main():
    log.info('OUTPUT_DIR is `%s`.', OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for entry in OUTPUT_DIR.iterdir():
        if entry.is_file():
            entry.unlink()
        else:
            shutil.rmtree(entry)

    for entry in (ROOT_LOC / 'static').iterdir():
        (shutil.copy if entry.is_file() else shutil.copytree)(entry, OUTPUT_DIR / entry.name)

    all_pages = [p for p in map(Page, CONTENT_DIR.glob('**/*.md')) if p.should_publish()]
    for page in all_pages:
        log.info('Rendering page %s.', repr(page))
        render(page.output_path(), page.meta.get('template', 'post.html'), post=page)

    posts = sorted((p for p in all_pages if p.date), key=lambda p: p.date, reverse=True)

    log.info('Rendering index page.')
    render('index.html', 'index.html', posts=posts)

    log.info('Rendering archive page.')
    render('archive.html', 'post-list.html', title='Archive', posts=posts)

    render_tags(posts)

    generate_feed(posts[:6], '/posts/index.xml')
    log.info('Finished')


def render_tags(posts):
    tagged_posts = defaultdict(list)

    for post in posts:
        for tag in post.tags:
            tagged_posts[tag].append(post)

    for tag, tag_posts in tagged_posts.items():
        log.info('Rendering tag page for `#%s`.', tag)
        render('tags/' + (tag + '.html'), 'post-list.html', title='Posts tagged #' + tag, tag=tag, posts=tag_posts)


def generate_feed(posts, path):
    fg = FeedGenerator()
    fg.id(Config.site_url)
    fg.title(Config.site_title)
    fg.author({'name': Config.author, 'email': Config.email})
    fg.link(href=Config.site_url + path, rel='self')
    fg.language('en')
    fg.description('Blog by Shrikant')

    for post in posts:
        fe = fg.add_entry()
        fe.id(post.permalink())
        fe.title(post.title())
        fe.description(post.body.split('\n\n', 1)[0])
        if post.date:
            fe.published(dt.datetime(post.date.year, post.date.month, post.date.day, tzinfo=dt.timezone.utc))

    fg.rss_file(str(OUTPUT_DIR / path.lstrip('/')))


if __name__ == '__main__':
    main()
