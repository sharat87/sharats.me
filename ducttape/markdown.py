import sys
import os
from collections import defaultdict
from pathlib import Path
import datetime as dt
import logging
import re
from html import unescape as html_unescape
import functools

import yaml
import markdown
import jinja2
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup


class MarkupSoup(BeautifulSoup):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('features', 'html.parser')
        super().__init__(*args, **kwargs)

    def __html__(self):
        return jinja2.Markup(str(self))


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

    soup = MarkupSoup(highlight(html_unescape(src), lexer, formatter))

    # Add a `data-lang` attribute with the language used for highlighting.
    for div in soup.find_all('div', class_='hl'):
        div.attrs['data-lang'] = cfg['lang']

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


def to_soup(md_content: str, dev_mode=False) -> MarkupSoup:
    html = markdown.markdown(
        md_content,
        extensions=['abbr', 'attr_list', 'def_list', 'footnotes', 'tables', 'sane_lists', 'toc', 'smarty', MdExt()],
        extension_configs={
            'toc': {
                'permalink': True,
            },
            'smarty': {
                'smart_quotes': False,
            },
        },
    )

    soup = MarkupSoup(html)

    # For all external pointing links, add `target=_blank`.
    for link in soup.find_all('a'):
        href = link.attrs['href']
        if href.startswith(('http://', 'https://')) and 'sharats.me' not in href and 'target' not in link:
            link.attrs['target'] = '_blank'

    # Add a h2 for table of contents, if any.
    for toc in soup.find_all('div', class_='toc'):
        toc.name = 'details'
        toc['open'] = ''
        toc.insert(0, MarkupSoup('<summary><h2>Table of Contents</h2></summary>'))

    # Tables need to be wrapped in a div so they can be horizontally scrolled on smaller screens.
    for table in soup.find_all('table'):
        table.wrap(soup.new_tag('div', attrs={'class': 'table-wrapper'}))

    for para in soup.find_all('p'):
        if not (para.string and para.string.lstrip().startswith(('TODO:', 'FIXME:', 'XXX:'))):
            continue

        if not dev_mode:
            raise ValueError('TODO marker found')

        para['style'] = 'background: #FFA; color: #C00; font-weight: 600; font-size: 1.3em;'

    # Convert code blocks with line numbers from tables to a pair of `div` elements.
    for table in soup.find_all('table', class_='hltable'):
        new_root = soup.new_tag('div', attrs={'class': 'hltable'})
        new_root.extend([d.extract() for d in table.find_all('div')])
        table.replace_with(new_root)

    fix_toc_markups(soup)

    # Syntax highlighting for inline code blocks.
    # for code in soup.find_all('code'):
    #     if not code.string:
    #         continue

    #     lexer = get_lexer_by_name('python')
    #     formatter = HtmlFormatter(
    #         cssclass='hl',
    #         wrapcode=False,
    #     )

    #     hl_soup = MarkupSoup(highlight(html_unescape(code.string), lexer, formatter), 'html.parser')
    #     code.clear()
    #     for child in list(hl_soup.pre.contents):
    #         code.append(child)
    #     if code.contents[-1].endswith('\n'):
    #         code.contents[-1].replace_with(code.contents[-1].rstrip('\n'))
    #     code['class'] = 'hl'

    check_attr_paragraphs(soup)

    return soup


def check_attr_paragraphs(soup):
    if soup.find_all('p', string=re.compile('^{: ')):
        raise ValueError('Messed up attr specifiers. Failing build.')


def fix_toc_markups(soup):
    # If the headers contain any `code` or `i` sub-elements, they are removed in the TOC links. I want them to be there,
    # so we copy the markup from headers back into the TOC links.
    for anchor in soup.select('.toc a'):
        anchor.clear()
        anchor.append(MarkupSoup(soup.select(anchor['href'])[0].decode_contents()))
