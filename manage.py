"""
Build my blog site. Just run `python manage.py build`.
"""

import sys
import os
from collections import defaultdict
from pathlib import Path
import datetime as dt
import logging
import re
import shutil
import time
import subprocess as sp
from html import unescape as html_unescape

import yaml
import jinja2
from feedgen.feed import FeedGenerator

from ducttape import markdown


class Config:
    site_url = 'https://sharats.me'
    site_title = "The Sharat's"
    author = 'Shrikant Sharat Kandula'
    email = 'shrikantsharat.k@gmail.com'
    feedburner_url = 'http://feeds.feedburner.com/sharats-me'

    twitter_user = 'sharat87'
    facebook_app_id = None

    dev_mode = False


# Auto load environment variables like `SCONFIG_DEV_MODE` or `SCONFIG_ADSENSE` etc.
for key, val in os.environ.items():
    if key.startswith('SCONFIG_'):
        setattr(Config, key[len('SCONFIG_'):].lower(), bool(int(val)))


# logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d %(message)s',
)
log = logging.getLogger(__name__)

ROOT_LOC = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_LOC / 'output'
CONTENT_DIR = ROOT_LOC / 'content'
TEMPLATES_DIR = ROOT_LOC / 'templates'
STATIC_DIR = ROOT_LOC / 'static'

env = jinja2.Environment(
    loader=jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        jinja2.FileSystemLoader(str(STATIC_DIR)),
    ]),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
)


def filter_en_join(items):
    return ', '.join(items[:-1]) + ((' and ' + items[-1]) if len(items) > 1 else '')


env.filters['en_join'] = filter_en_join


class Page:
    def __init__(self, path):
        self.path = path.resolve()
        self.slug = self.path.stem
        self.meta = {
            'publish': True,
            'comments': True,
        }
        self.tags = []  # This should conceptually be a set, but we use list so the order of the tags is predictable.
        self.date = None
        self.content = None

    @property
    def title(self):
        soup = markdown.to_soup(self.meta['title'], Config.dev_mode)
        soup.p.name = 'span'
        return soup

    @property
    def link(self) -> str:
        return '/' + str(self.output_path.parent).replace('\\', '/').strip('/') + '/'

    @property
    def permalink(self) -> str:
        return Config.site_url + self.link

    @property
    def output_path(self) -> Path:
        return self.path.relative_to(CONTENT_DIR).with_name(self.slug) / 'index.html'

    @property
    def depth(self):
        return len(self.path.relative_to(CONTENT_DIR).parts)

    @property
    def date_display(self):
        return self.date.strftime('%d %b, %Y').lstrip('0') if self.date else ''

    @property
    def date_iso(self):
        return self.date.isoformat() if self.date else ''

    @property
    def should_publish(self):
        return self.meta['publish'] and (self.date is None or self.date <= today())

    @property
    def last_mod(self):
        return self.meta.get('modified_date', self.date)

    @property
    def layout(self):
        layout = self.meta.get('layout')
        if layout:
            return layout

        folder_name = self.path.relative_to(CONTENT_DIR).parent.name
        if folder_name:
            if folder_name.endswith('es'):
                return folder_name[:-2]
            elif folder_name.endswith('s'):
                return folder_name[:-1]
            return folder_name

        return 'page'

    def __str__(self):
        return f'<{self.__class__.__name__} {self.slug} {self.layout}>'

    __repr__ = __str__


def load_page(page):
    log.info('Loading page %r.', page)
    page.raw_body = page.path.read_text('utf8', 'strict')

    if page.raw_body.startswith('---\n'):
        meta_block, page.raw_body = page.raw_body[4:].split('\n---\n', 1)
        page.meta.update(yaml.safe_load(meta_block))
        if 'tags' in page.meta:
            page.tags.extend(page.meta.pop('tags'))

    page.body = env.from_string(page.raw_body).render(config=Config) if page.meta.get('render_content') else page.raw_body

    match = re.fullmatch(r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>[-\w]+)', page.slug)
    if match:
        page.date = dt.datetime.fromisoformat(match.group('date')).date()
        page.slug = match.group('slug')

    if Config.dev_mode or page.should_publish:
        page.html_body = markdown.to_soup(page.body, Config.dev_mode)

    log.info('Loaded page %r.', page)


def foreach(fn, max_threads=0):
    """
    Returns a function that taks a list of pages and calles `fn` on each page. If `max_threads` is non-zero, that many
    threads will be spawned to do the work instead.
    """

    if not max_threads:
        return lambda ps: list(map(fn, ps))

    from threading import Thread
    from queue import Queue, Empty

    def thread_target(q, results):
        while True:
            try:
                results.append(fn(q.get(False)))
            except Empty:
                return

    def processor(all_pages):
        page_q = Queue()
        for page in all_pages:
            page_q.put(page)

        threads = []
        results = []
        for _ in range(max_threads):
            th = Thread(target=thread_target, args=(page_q, results))
            threads.append(th)
            th.start()

        for th in threads:
            th.join()

        return results

    return processor


def filter_by(fn):
    def proc(pages):
        for i in reversed([i for i, p in enumerate(pages) if not fn(p)]):
            del pages[i]
    return proc


def render(target, template, **kwargs):
    markup = env.get_template(template).render(config=Config, **kwargs)
    dest = OUTPUT_DIR / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding='utf-8')


def render_page(page):
    log.info('Rendering page %r.', page)
    page.content = env.get_template(page.meta.get('template', 'page.html')).render(config=Config, page=page)


def render_pdf(page):
    if not page.meta.get('pdf', False):
        return

    import weasyprint
    html_file = OUTPUT_DIR / page.output_path
    html_file.parent.mkdir(parents=True, exist_ok=True)

    def url_fetcher(url):
        if url.startswith('http'):
            return {'string': b''}
        if url.startswith('file://'):
            # Strip `file://`.
            url = url[len('file://'):]
            # Turn it into an absolute path.
            url = (OUTPUT_DIR / url[1:]) if url.startswith('/') else (html_file.parent / url)
            # Add `file://` after turning into a Linux-style absolute path. Yeah, that's needed.
            url = 'file://' + str(url).split(':')[-1].replace('\\', '/')
        return weasyprint.default_url_fetcher(url)

    try:
        doc = weasyprint.HTML(
            string=page.content + '\n' + '<style>' + Path('pdf.css').read_text('utf8', 'strict') + '</style>',
            base_url=str(OUTPUT_DIR),
            url_fetcher=url_fetcher,
        )
        doc.write_pdf(html_file.parent.with_suffix('.pdf'))
    except:
        pass


def sort_by_date(pages):
    pages.sort(key=lambda p: (p.date or dt.date(2000, 1, 1)))


def write_page(page):
    if page.content:
        log.info('Writing page to %r.', page.output_path)
        dest = OUTPUT_DIR / page.output_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page.content, encoding='utf8')


def today() -> dt.date:
    return dt.datetime.utcnow().date()


def action_build():
    # The *ducttape* static site generator.
    start_time = time.time()
    log.info('BUILD DATE: %r', today())
    log.info('OUTPUT_DIR is %r.', OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    action_clean()

    for entry in STATIC_DIR.iterdir():
        (shutil.copy if entry.is_file() else shutil.copytree)(entry, OUTPUT_DIR / entry.name)

    processors = [
        foreach(load_page, 3),
        None if Config.dev_mode else filter_by(lambda p: p.should_publish),
        sort_by_date,
        foreach(render_page),
        render_site_level_pages,
        foreach(write_page),
        foreach(render_pdf),
    ]

    all_pages = [Page(p) for p in CONTENT_DIR.glob('**/*.md')]
    for fn in processors:
        if fn is not None:
            fn(all_pages)

    log.info('Built %d pages in %.2f seconds.', len(all_pages), time.time() - start_time)


def render_site_level_pages(all_pages):
    posts = sorted((p for p in all_pages if p.layout == 'post'), key=lambda p: p.date, reverse=True)

    log.info('Rendering index page.')
    render('index.html', 'index.html', posts=posts)

    log.info('Rendering all posts page.')
    render('posts/index.html', 'post-list.html', title='Archive', posts=posts)

    render_tags(posts)

    render('sitemap.html', 'sitemap.html', title='Sitemap', page_groups=page_tree(all_pages))
    render('sitemap.xml', 'sitemap.xml', pages=all_pages)
    if not Config.dev_mode:
        sp.run(['gzip', '-k', 'sitemap.xml'], cwd=str(OUTPUT_DIR))

    generate_feed(posts[:6], '/posts/index.xml')


def render_tags(posts):
    tagged_posts = defaultdict(list)

    for post in posts:
        for tag in post.tags:
            tagged_posts[tag].append(post)

    render('tags/index.html', 'tag-list.html', title='Tags', tagged_posts=tagged_posts)
    for tag, tag_posts in tagged_posts.items():
        log.info('Rendering tag page for `#%s`.', tag)
        render('tags/' + tag + '/index.html', 'post-list.html', title='Posts tagged #' + tag, tag=tag, posts=tag_posts)


def page_tree(pages):
    groups = []
    prev_depth = 0

    for page in sorted(pages, key=lambda p: p.path):
        if page.depth > prev_depth:
            if prev_depth > 0:
                groups.append(('text', page.path.parent.stem.title()))
            groups.append(('open', page))
        elif page.depth < prev_depth:
            groups.append(('close', page))
        else:
            groups.append(('link', page))

        prev_depth = page.depth

    return groups


def generate_feed(posts, path):
    fg = FeedGenerator()
    fg.id(Config.site_url)
    fg.title(Config.site_title)
    fg.author({'name': Config.author, 'email': Config.email})
    fg.link(href=Config.site_url + '/posts/', rel='self')
    fg.language('en')
    fg.description('A blog about software and non-software.')
    fg.copyright('Copyright 2010-2020, Shrikant Sharat Kandula')

    for post in posts:
        fe = fg.add_entry()
        fe.id(post.permalink)
        fe.title(re.sub(r'</?\w+>', '', str(post.title)))  # Could use `striptags` filter once we move to Jinja2.
        fe.description(post.body.split('\n\n', 1)[0])
        if post.date:
            fe.published(dt.datetime(post.date.year, post.date.month, post.date.day, tzinfo=dt.timezone.utc))

    fg.rss_file(str(OUTPUT_DIR / path.lstrip('/')))


def files_to_watch():
    for path in [CONTENT_DIR, TEMPLATES_DIR, ROOT_LOC / 'static']:
        yield from filter(Path.is_file, path.glob('**/*'))


def action_watch():
    log.info('Overriding `dev_mode` to True.')
    Config.dev_mode = True

    mtimes = {}
    for file in files_to_watch():
        mtimes[file] = file.stat().st_mtime

    action_build()
    log.info('Watching %r files ...O_O...', len(mtimes))

    while True:
        changed_files = set()
        missing_files = set(mtimes.keys())
        for file in files_to_watch():
            cur_mtime = file.stat().st_mtime
            if cur_mtime > mtimes.get(file, 0):
                changed_files.add(file)
            if file in missing_files:
                missing_files.remove(file)
            mtimes[file] = cur_mtime

        if changed_files or missing_files:
            log.info('changed_files %r', changed_files)
            log.info('missing_files %r', missing_files)

            action_build()

            for f in missing_files:
                del mtimes[f]

            log.info('Back to watching %r files ...O_O...', len(mtimes))

        time.sleep(1)


def action_clean():
    if OUTPUT_DIR.is_dir():
        for entry in OUTPUT_DIR.iterdir():
            if entry.is_file():
                entry.unlink()
            else:
                shutil.rmtree(entry)


def action_serve():
    import http.server
    from functools import partial
    http.server.test(
        HandlerClass=partial(http.server.SimpleHTTPRequestHandler, directory=str(OUTPUT_DIR)),
        port=8010,
        bind='',
    )


def action_develop():
    """Watch and serve"""
    from threading import Thread
    Thread(target=action_watch, name='watcher', daemon=True).start()
    action_serve()


def action_check_deps():
    """Check if the dependencies from requirements.txt are the latest versions."""
    raise NotImplementedError


def main():
    log.info('Python %s', sys.version)
    globals()['action_' + sys.argv[1]]()


if __name__ == '__main__':
    main()
