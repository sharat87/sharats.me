import os.path
from pathlib import Path
import logging
import re
import datetime
import jinja2
import mistune


"""
TODO:
- Articles with reddit tag should have reddit voting buttons on them.
"""


class Post:
    def __init__(self, path):
        self.path = path

        match = re.fullmatch(r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>[-\w]+)\.md', path.name)
        self.date = datetime.datetime.fromisoformat(match.group('date')).date()
        self.slug = match.group('slug')

        self.raw = self.path.read_text()
        meta, body = self.raw.split('\n\n', 1)
        self.body = body.strip()

        self.meta = {}
        self.title = self.tags = None
        for line in meta.splitlines():
            key, value = line.split(':', 1)
            if key == 'tags':
                self.tags = [v.strip() for v in value.split(',')]
            elif key == 'title':
                self.title = value.strip()
            else:
                self.meta[key] = value.strip()

        self.html_body = mistune.markdown(self.body)

    def __str__(self):
        return f'<Post {self.slug}>'

    __repr__ = __str__


def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)

    SCRIPT_LOC = Path(os.path.abspath(__file__))
    ROOT_LOC = SCRIPT_LOC.parent
    OUTPUT_DIR = ROOT_LOC / 'output'
    log.info('OUTPUT_DIR is `%s`', OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = []
    for post_path in list((ROOT_LOC / 'posts').glob('*.md')):
        posts.append(Post(post_path))

    log.info('posts is `%s`', repr(posts))

    env = jinja2.Environment(
        loader=jinja2.PackageLoader(__name__, 'templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    (OUTPUT_DIR / 'index.html').write_text(env.get_template('index.html').render(posts=posts))


if __name__ == '__main__':
    main()
