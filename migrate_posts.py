"""
A small script to copy my website assets from the original folder to this 11ty implementation.
"""

from pathlib import Path
import os
import shutil


ORIGINAL_ROOT = Path('C:/labs/sharats.me')


def _main():
    # copy('static/styles.css', 'css/')
    # copy('static/favicon.ico')
    # copy('static/favicon-16x16.png', 'icons/')

    # shutil.copytree(ORIGINAL_ROOT / 'static', 'static')

    for md_path in ORIGINAL_ROOT.glob('content/posts/*.md'):
        migrate_md(md_path, Path('posts') / md_path.name)


def copy(src, dst='.'):
    if dst and not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst))
    shutil.copy2(ORIGINAL_ROOT / src, dst)


def migrate_fence_config(fence_config):
    return fence_config.replace('linenos:', '"linenos":').replace('filename:', '"filename":').replace(" yes", " true")


def migrate_md(src, dst):
    content = src.read_text(encoding='utf8')

    in_block = False
    in_script = False

    final_lines = []
    for line in content.splitlines():
        if line == '<script>':
            in_script = True

        elif line == '</script>':
            in_script = False

        if '{%' in line or '#}' in line:
            line = (' ' * (len(line) - len(line.lstrip()))) + '{% raw %}' + line.strip() + '{% endraw %}'

        if in_block:
            if not line or line.startswith(' ' * 4):
                final_lines.append(line[4:])
            else:
                if not final_lines[-1]:
                    final_lines.insert(len(final_lines) - 1, '```')
                else:
                    final_lines.append('```')
                final_lines.append(line)
                in_block = False

        elif line.startswith('    :::'):
            in_block = True
            code_config = migrate_fence_config(line[7:])
            final_lines.append('```' + code_config)

        elif line.startswith('```') and ' ' in line:
            final_lines.append(migrate_fence_config(line))

        elif in_script and not line:
            continue

        else:
            final_lines.append(line)

    dst.write_text('\n'.join(final_lines), encoding='utf8')


if __name__ == '__main__':
    _main()
