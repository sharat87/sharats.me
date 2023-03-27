import re
import shlex
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import SimpleTagInlineProcessor


class ImageLinks(Preprocessor):
    def run(self, lines):
        new_lines = []
        i_max = len(lines) - 1

        for i, line in enumerate(lines):
            if (i == 0 or not lines[i - 1]) and (i == i_max or not lines[i + 1]):
                match = re.match(r"^!\[.+?]\((.+?)\)$", line)
                if match:
                    new_lines.append("[" + line + "](" + match.group(1) + ")")
                    new_lines.append("{: .img }")
                    continue

            new_lines.append(line)

        return new_lines


class FenceConfigs(Preprocessor):
    """
    Brace-less syntax for configuring fence blocks, so syntax highlighting still works in Vim.
    """

    def run(self, lines):
        for i, line in enumerate(lines):
            match = re.match(r"^```(?P<lang>\w+)\s+(?P<conf>.+)", line)
            if match is None:
                continue
            parts = shlex.split(match.group("conf"))

            modified_parts = []
            for part in parts:
                key, value = part.split("=", 1)
                if key == "hl_lines":
                    # Range syntax is not working for `hl_lines`, for some reason. So we convert them to flat list of line numbers.
                    value = re.sub(
                        r"(\d+)-(\d+)",
                        lambda m: " ".join(map(str, range(int(m[1]), 1 + int(m[2])))),
                        value,
                    )
                modified_parts.append(key + "=\"" + value + "\"")

            lines[i] = "```{ ." + match.group("lang") + " " + " ".join(modified_parts) + " }"

        return lines


class ExternalLinks(Treeprocessor):
    """
    For all absolute links (i.e., links with a http or https protocol), add the target=_blank and rel attributes.
    """

    def run(self, root):
        for el in root.iter("a"):
            href = el.get("href", "")
            # TODO: Check that the host isn't `sharats.me` or `localhost`.
            if re.match(r"^https?://", href):
                el.attrib.update(rel="noopener noreferrer", target="_blank")
            elif href.startswith("/"):
                # Needed for links in PDFs.
                el.attrib.update(href="https://sharats.me" + href)


class TableWrapper(Treeprocessor):
    """
    Wrap all tables in a `div.table-wrapper` so that horizontal scrolling of tables is possible.
    """

    def run(self, root):
        for el in root.findall("table"):
            el.tag = "div"
            el.attrib["class"] = "table-wrapper"
            table = etree.SubElement(el, "table")
            for child in el.findall("*"):
                if child is not table:
                    el.remove(child)
                    table.append(child)


class VideoProcessor(BlockProcessor):
    """
    Embedded Videos! Use by writing a paragraph with a single line like this:

        Video: link-to-video-here.mp4

    This will be turned into a nice video widget.
    """

    RE = re.compile(r"^Video:\s*(?P<url>[-\w.:/]+)\.?$")

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m is None:
            # This should never happen, but just in case...
            print("We've got a problem video: %r" % block)
            return

        h = etree.SubElement(parent, "video")
        url = m.group("url").strip()
        if not url.startswith(("http://", "https://", "//")):
            url = "{static}/static/" + url

        h.attrib.update(
            src=url,
            muted="",
            playsinline="",
            preload="",
            controls="",
        )
        h.text = "Your browser does not support HTML5 video. Here's "
        a = etree.SubElement(h, "a", href=url)
        a.text = "a link to the video"
        a.tail = "instead."


class SharatsExt(Extension):
    def extendMarkdown(self, md):
        # Ref: <https://python-markdown.github.io/extensions/api/>.
        md.preprocessors.register(ImageLinks(md), "img_links", 200)
        md.preprocessors.register(FenceConfigs(md), "fence_configs", 200)
        md.treeprocessors.register(ExternalLinks(md), "ext_links", 20)
        md.treeprocessors.register(TableWrapper(md), "table_wrapper", 21)
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~(.+?)~~", "del"), "del", 175)
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()\(\((.+?)\)\)", "kbd"), "kbd", 175)
        md.parser.blockprocessors.register(VideoProcessor(md.parser), "video", 175)


# This function will be called by python-markdown to get an instance of the extension.
def makeExtension(**kwargs):
    return SharatsExt(**kwargs)


# Monkey patching for table-less code-blocks with line numbers.
import pygments.formatters.html
import markdown.extensions.codehilite
import hashlib
from collections import defaultdict
class CustomFormatter(pygments.formatters.html.HtmlFormatter):
    def __init__(self, _, **kwargs):
        super().__init__(**kwargs)
        self.is_linenos_enabled = self.linenos > 0
        # Disable the default table linenos wrapping.
        self.linenos = 0

    def wrap(self, source, output=None):
        if self.wrapcode:
            source = self._wrap_code(source)
        return self.grid_wrap(source)

    def grid_wrap(self, source):
        source = list(source)
        line_count = sum(item[0] for item in source)
        should_collapse = line_count > 25
        input_id = "co-" + dum_hash(source)

        if should_collapse:
            yield 0, f'<input type=checkbox id={input_id}>'

        if self.filename:
            yield 0, '<div class=filename><span>' + self.filename + '</span></div>'

        if self.is_linenos_enabled:
            yield 0, (
                '<pre class="linenos">' +
                "\n".join(f'{"<div class=collapse>" if should_collapse and n == 21 else ""}<span>{n}</span>' for n in range(1, 1 + line_count)) +
                ('</div>' if should_collapse else '') +
                '</pre>'
            )

        yield 0, '<pre class="content">'

        line_no = 1
        for t, line in source:
            if should_collapse and line_no == 21:
                line = '<div class=collapse>' + line
            yield t, line
            line_no += t

        yield 0, ('</div>' if should_collapse else '') + '</pre>'

        if should_collapse:
            yield 0, f'<label for={input_id}><span class="btn show-full-code-btn">Show remaining {line_count - 20} lines</span></label>'

        yield 0, '<div class="btns"></div>'


hash_counts = defaultdict(int)
def dum_hash(lines):
    value = hashlib.md5(''.join(l for _, l in lines).encode()).hexdigest()
    hash_counts[value] += 1
    value += str(hash_counts[value])
    return value

markdown.extensions.codehilite.get_formatter_by_name = CustomFormatter
