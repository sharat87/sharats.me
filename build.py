from pathlib import Path
import logging
import re
import datetime
import jinja2
from collections import defaultdict
import shutil

import mistune
from mistune_contrib.toc import TocMixin
from mistune_contrib.highlight import HighlightMixin
from feedgen.feed import FeedGenerator


"""
For math support, checkout mistune_contrib's math mixin at https://github.com/lepture/mistune-contrib/blob/master/mistune_contrib/math.py
"""


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

env = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__),
    autoescape=jinja2.select_autoescape(['html']),
)


class Post:
    def __init__(self, path):
        self.path = path

        match = re.fullmatch(r'((?P<date>\d{4}-\d{2}-\d{2})_)?(?P<slug>[-\w]+)\.md', path.name)
        if match.group('date'):
            self.date = datetime.datetime.fromisoformat(match.group('date')).date()
        else:
            self.date = None

        self.slug = match.group('slug')

        body = self.path.read_text()
        self.meta = {}

        while True:
            match = re.match(r'(\w+):\s*(.*?)\n', body)
            if match is None:
                break
            body = body[match.end():]
            key, value = match.group(1), match.group(2)
            self.meta[key] = value.strip()

        self.title = self.meta.pop('title') or self.slug.title()
        self.tags = [v for v in map(str.strip, self.meta.pop('tags', '').split(',')) if v]
        self.body = body
        self.html_body = md_to_html(body)

    @property
    def link(self):
        return f'/posts/{self.slug}.html'

    @property
    def permalink(self):
        return Config.site_url + self.link

    @property
    def date_display(self):
        return self.date.strftime('%b %d, %Y')

    @property
    def date_iso(self):
        return self.date.isoformat()

    def __str__(self):
        return f'<Post {self.slug}>'

    __repr__ = __str__


class Markdown(TocMixin, HighlightMixin, mistune.Renderer):
    _md = None


def md_to_html(md_content):
    if Markdown._md is None:
        Markdown._md = mistune.Markdown(renderer=Markdown())
        Markdown._md.renderer.options.update(inlinestyles=False, linenos=False)

    Markdown._md.renderer.reset_toc()
    html = Markdown._md(md_content)
    if Markdown._md.renderer.toc_tree:
        html = html.replace('<!-- TOC -->', Markdown._md.renderer.render_toc(level=3))

    return html


def render(target, template, **kwargs):
    (OUTPUT_DIR / target).write_text(env.get_template(template).render(config=Config, **kwargs))


def main():
    log.info('OUTPUT_DIR is `%s`.', OUTPUT_DIR)
    for entry in OUTPUT_DIR.iterdir():
        if entry.is_file():
            entry.unlink()
        else:
            shutil.rmtree(entry)

    (OUTPUT_DIR / 'posts').mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'tags').mkdir(parents=True, exist_ok=True)

    posts = []
    for post_path in list((ROOT_LOC / 'posts').glob('*.md')):
        posts.append(Post(post_path))

    posts.sort(key=lambda p: p.date, reverse=True)
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

    for page_path in list((ROOT_LOC / 'pages').glob('*.md')):
        page = Post(page_path)
        log.info('Rendering page %s.', repr(page))
        render(page.slug + '.html', page.meta.get('template', 'post.html'), post=page)

    tagged_posts = defaultdict(list)

    for post in posts:
        log.info('Rendering `%s`.', repr(post))
        render('posts/' + (post.slug + '.html'), 'post.html', post=post)
        for tag in post.tags:
            tagged_posts[tag].append(post)

    for tag, tag_posts in tagged_posts.items():
        log.info('Rendering tag page for `#%s`.', tag)
        render('tags/' + (tag + '.html'), 'post-list.html', title='Posts tagged #' + tag, tag=tag, posts=tag_posts)

    fg = FeedGenerator()
    fg.id(Config.site_url)
    fg.title(Config.site_title)
    fg.author({'name': Config.author, 'email': Config.email})
    fg.link(href='https://www.sharats.me/posts/index.xml', rel='self')
    fg.language('en')
    fg.description('Blog by Shrikant')

    for post in posts[:6]:
        fe = fg.add_entry()
        fe.id(post.permalink)
        fe.title(post.title)
        fe.description(post.body.split('\n\n', 1)[0])

    fg.rss_file(str(OUTPUT_DIR / 'posts' / 'index.xml'))


if __name__ == '__main__':
    main()
