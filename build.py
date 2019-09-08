"""
Build my blog site. No command line arguments. Just run `python build.py`.

For math support, checkout mistune_contrib's math mixin at
https://github.com/lepture/mistune-contrib/blob/master/mistune_contrib/math.py
"""

from collections import defaultdict
from pathlib import Path
import datetime
import logging
import re
import shutil

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

env = jinja2.Environment(loader=jinja2.PackageLoader(__name__), autoescape=jinja2.select_autoescape(['html', 'xml']))

markdown = mistune.Markdown(renderer=type('Renderer', (TocMixin, HighlightMixin, mistune.Renderer), {})())
markdown.renderer.options.update(inlinestyles=False, linenos=False)


class Page:
    def __init__(self, path):
        self.path = path
        self.slug = path.stem
        body = self.path.read_text()
        self.meta = {}

        while True:
            match = re.match(r'(\w+):\s*(.*?)\n', body)
            if match is None:
                break
            body = body[match.end():]
            key, value = match.group(1), match.group(2)
            self.meta[key.lower()] = value.strip()

        self.tags = [v for v in map(str.strip, self.meta.pop('tags', '').split(',')) if v]
        self.body = body
        self.html_body = md_to_html(body)

    @property
    def title(self):
        return self.meta.get('title') or self.slug.title()

    @property
    def link(self):
        return f'/posts/{self.slug}.html'

    @property
    def permalink(self):
        return Config.site_url + self.link

    @property
    def output_path(self):
        return self.slug + '.html'

    def __str__(self):
        return f'<{self.__class__.__name__} {self.slug}>'

    __repr__ = __str__


class Post(Page):
    def __init__(self, path):
        super().__init__(path)

        match = re.fullmatch(r'((?P<date>\d{4}-\d{2}-\d{2})_)?(?P<slug>[-\w]+)', self.slug)
        self.date = datetime.datetime.fromisoformat(match.group('date')).date()
        self.slug = match.group('slug')

    @property
    def date_display(self):
        return self.date.strftime('%b %d, %Y')

    @property
    def date_iso(self):
        return self.date.isoformat()

    @property
    def output_path(self):
        return 'posts/' + super().output_path


def md_to_html(md_content: str):
    markdown.renderer.reset_toc()
    html = markdown(md_content)
    if markdown.renderer.toc_tree and '<!-- TOC -->' in html:
        html = html.replace('<!-- TOC -->', markdown.renderer.render_toc(level=3))
    return html


def render(target, template, **kwargs):
    markup = env.get_template(template).render(config=Config, **kwargs)
    (OUTPUT_DIR / target).write_text(markup, encoding='utf-8')


def main():
    log.info('OUTPUT_DIR is `%s`.', OUTPUT_DIR)
    for entry in OUTPUT_DIR.iterdir():
        if entry.is_file():
            entry.unlink()
        else:
            shutil.rmtree(entry)

    (OUTPUT_DIR / 'posts').mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'tags').mkdir(parents=True, exist_ok=True)

    posts = sorted((Post(p) for p in (ROOT_LOC / 'posts').glob('*.md')), key=lambda p: p.date, reverse=True)
    log.info('posts is `%s`.', repr(posts))

    for entry in (ROOT_LOC / 'static').iterdir():
        if entry.is_file():
            shutil.copy(entry, OUTPUT_DIR)
        else:
            raise NotImplementedError('Copying static directories is WIP.')

    log.info('Rendering index page.')
    render('index.html', 'index.html', posts=posts)

    log.info('Rendering archive page.')
    render('archive.html', 'post-list.html', title='Archive', posts=posts)

    render_pages(map(Page, (ROOT_LOC / 'pages').glob('*.md')))
    render_pages(posts)
    render_tags(posts)

    generate_feed(posts[:6], '/posts/index.xml')
    log.info('Finished')


def render_pages(pages):
    for page in pages:
        log.info('Rendering page %s.', repr(page))
        render(page.output_path, page.meta.get('template', 'post.html'), post=page)


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
        fe.id(post.permalink)
        fe.title(post.title)
        fe.description(post.body.split('\n\n', 1)[0])

    fg.rss_file(str(OUTPUT_DIR / path.lstrip('/')))


if __name__ == '__main__':
    main()
