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
import markdown
from feedgen.feed import FeedGenerator
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup


def read_env(name, default):
    val = os.getenv(name, '')
    return bool(int(val)) if val.isdigit() else default


class Config:
    site_url = 'https://www.sharats.me'
    site_title = "The Sharat's"
    author = 'Shrikant Sharat Kandula'
    email = 'shrikantsharat.k@gmail.com'
    feedburner_url = 'http://feeds.feedburner.com/sharats-me'

    dev_mode = read_env('DEV', False)

    adsense = read_env'ADSENSE', True)


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

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
)


def filter_en_join(items):
    return ', '.join(items[:-1]) + ((' and ' + items[-1]) if len(items) > 1 else '')


env.filters['en_join'] = filter_en_join


class Page:
    def __init__(self, path):
        self.path = path
        self.slug = path.stem
        self.meta = {
            'publish': True,
            'comments': True,
        }
        self.tags = []  # This should conceptually be a set, but we use list so the order of the tags is predictable.
        self.date = None

        body = self.path.read_text()

        if body.startswith('---\n'):
            meta_block, body = body[4:].split('\n---\n', 1)
            self.meta.update(yaml.safe_load(meta_block))
            if 'tags' in self.meta:
                self.tags.extend(self.meta.pop('tags'))

        self.body = body
        self.html_body = md_to_html(body)

        match = re.fullmatch(r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>[-\w]+)', self.slug)
        if match:
            self.date = dt.datetime.fromisoformat(match.group('date')).date()
            self.slug = match.group('slug')

    @property
    def title(self):
        return md_to_html(self.meta.get('title') or self.slug.title())[3:-4]  # Strip the <p> tag.

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
        return self.date.strftime('%b %d, %Y') if self.date else ''

    @property
    def date_iso(self):
        return self.date.isoformat() if self.date else ''

    @property
    def should_publish(self):
        return Config.dev_mode or (self.meta['publish'] and (self.date is None or self.date <= dt.date.today()))

    @property
    def last_mod(self):
        return self.meta.get('modified_date', self.date)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.slug}>'

    __repr__ = __str__


class CodeHighlighter(markdown.treeprocessors.Treeprocessor):
    """
    Originally taken from the official *codehilite* extension.
    """

    def run(self, doc):
        for block in doc.iter('pre'):
            if len(block) == 1 and block[0].tag == 'code':
                self.highlight_code(block)

    def highlight_code(self, block):
        src = block[0].text
        cfg = {'lang': 'text', 'linenos': False}

        if src.startswith((':::', '#!')):
            spec, src = src.split('\n', 1)
            match = re.match(r'^(?P<marker>:::|#!)(?P<lang>\w+)(\s+(?P<cfg>.+))?', spec)
            cfg['linenos'] = match.group('marker') == '#!'
            cfg['lang'] = match.group('lang')
            if match.group('cfg'):
                cfg.update(yaml.safe_load(match.group('cfg')))

        markup = highlight_code_block(src, cfg)

        placeholder = self.md.htmlStash.store(markup)
        # Clear codeblock in etree instance
        block.clear()
        # Change to p element which will later
        # be removed when inserting raw markup
        block.tag = 'p'
        block.text = placeholder


def highlight_code_block(src, cfg):
    lexer = get_lexer_by_name(cfg['lang'])
    formatter = HtmlFormatter(
        linenos=cfg.get('linenos', False),
        cssclass='hl',
        hl_lines=cfg.get('hl_lines') or [],
        filename=cfg.get('filename'),
        wrapcode=True,  # Wrap code in <code> tags, as recommended by HTML5 spec.
    )

    soup = BeautifulSoup(highlight(html_unescape(src), lexer, formatter), 'html.parser')

    # Add a `data-lang` attribute with the language used for highlighting.
    for div in soup.find_all('div', class_='hl'):
        div.attrs['data-lang'] = cfg['lang']

    # Convert code blocks with line numbers from tables to a pair of `div` elements.
    for table in soup.find_all('table', class_='hltable'):
        new_root = soup.new_tag('div', attrs={'class': 'hltable'})
        new_root.extend([d.extract() for d in table.find_all('div')])
        table.replace_with(new_root)

    return str(soup)


class CodeHighlighterFence(markdown.preprocessors.Preprocessor):
    FENCED_BLOCK_RE = re.compile(r'''
            (?P<fence>^(?:~{3}|`{3}))      # Opening ``` or ~~~
            (?P<lang>\w*)                  # Optional lang
            (?:[ ]+(?P<cfg>.+?))?[ ]*\n     # Optional config
            (?P<code>.*?)(?<=\n)
            (?P=fence)$''',
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """

        text = '\n'.join(lines)

        while 1:
            match = self.FENCED_BLOCK_RE.search(text)
            if not match:
                break

            cfg = {'lang': match.group('lang') or 'text'}
            if match.group('cfg'):
                cfg.update(yaml.safe_load(match.group('cfg')))

            markup = highlight_code_block(match.group('code'), cfg)
            placeholder = self.md.htmlStash.store(markup)

            text = '\n'.join([text[:match.start()], placeholder, text[match.end():]])

        return text.split('\n')


class MdExt(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(CodeHighlighter(md), 'code_highlighter', 30)
        md.preprocessors.register(CodeHighlighterFence(md), 'code_highlighter_fence', 25)
        md.registerExtension(self)


def md_to_html(md_content: str) -> str:
    return markdown.markdown(
        md_content,
        extensions=['abbr', 'attr_list', 'def_list', 'footnotes', 'tables', 'sane_lists', 'toc', MdExt()],
        extension_configs={
            'toc': {
                'permalink': True,
            }
        },
    )


def render(target, template, **kwargs):
    markup = env.get_template(template).render(config=Config, **kwargs)
    dest = OUTPUT_DIR / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding='utf-8')


def action_build():
    start_time = time.time()
    log.info('OUTPUT_DIR is `%s`.', OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    action_clean()

    for entry in (ROOT_LOC / 'static').iterdir():
        (shutil.copy if entry.is_file() else shutil.copytree)(entry, OUTPUT_DIR / entry.name)

    all_pages = [p for p in map(Page, CONTENT_DIR.glob('**/*.md')) if p.should_publish]
    for page in all_pages:
        log.info('Rendering page %s.', repr(page))
        render(page.output_path, page.meta.get('template', 'post.html'), post=page)

    posts = sorted((p for p in all_pages if p.date), key=lambda p: p.date, reverse=True)

    log.info('Rendering index page.')
    render('index.html', 'index.html', posts=posts)

    log.info('Rendering archive page.')
    render('archive/index.html', 'post-list.html', title='Archive', posts=posts)

    render_tags(posts)

    render('sitemap.html', 'sitemap.html', title='Sitemap', page_groups=page_tree(all_pages))
    render('sitemap.xml', 'sitemap.xml', pages=all_pages)
    if not Config.dev_mode:
        sp.run(['gzip', '-k', 'sitemap.xml'], cwd=str(OUTPUT_DIR))

    generate_feed(posts[:6], '/posts/index.xml')
    log.info('Build finished in {:.2f} seconds.'.format(time.time() - start_time))


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
    fg.link(href=Config.site_url + '/archive.html', rel='self')
    fg.language('en')
    fg.description('A blog about software and non-software.')
    fg.copyright('Copyright 2010-2020, Shrikant Sharat Kandula')

    for post in posts:
        fe = fg.add_entry()
        fe.id(post.permalink)
        fe.title(re.sub(r'</?\w+>', '', post.title))
        fe.description(post.body.split('\n\n', 1)[0])
        if post.date:
            fe.published(dt.datetime(post.date.year, post.date.month, post.date.day, tzinfo=dt.timezone.utc))

    fg.rss_file(str(OUTPUT_DIR / path.lstrip('/')))


def files_to_watch():
    for path in [CONTENT_DIR, TEMPLATES_DIR, ROOT_LOC / 'static']:
        yield from (file for file in path.glob('**/*') if file.is_file())


def action_watch():
    mtimes = {}
    for file in files_to_watch():
        mtimes[file] = file.stat().st_mtime

    action_build()
    log.info('Watching %r files ...O_O...', len(mtimes))

    while True:
        changed_files = set()
        missing_files = set(mtimes.keys())
        for file in files_to_watch():
            if file not in mtimes or file.stat().st_mtime > mtimes[file]:
                changed_files.add(file)
                mtimes[file] = file.stat().st_mtime
            missing_files.remove(file)

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


def main():
    log.info('Python %s', sys.version)
    globals()['action_' + sys.argv[1]]()


if __name__ == '__main__':
    main()
