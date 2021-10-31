import json
import re
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
                match = re.match(r"^!\[.+?\]\((.+?)\)$", line)
                if match:
                    new_lines.append("[" + line + "](" + match.group(1) + ")")
                    new_lines.append("{: .img }")
                    continue

            new_lines.append(line)

        return new_lines


class FenceConfigs(Preprocessor):
    def run(self, lines):
        new_lines = []

        for i, line in enumerate(lines):
            match = re.match(r"^```\s*(?P<lang>\w+)\s+(?P<conf>.+)", line)

            if match:
                conf = json.loads(match.group("conf"))

                parts = ["```{", "." + match.group("lang")]
                if conf.get("linenos"):
                    parts.append("linenos=true")
                if conf.get("filename"):
                    parts.append('filename="' + conf["filename"] + '"')
                parts.append("}")
                line = " ".join(parts)

            new_lines.append(line)

        return new_lines


class ExternalLinks(Treeprocessor):
    def run(self, root):
        for el in root.iter("a"):
            href = el.attrib["href"]
            if href and re.match(r"^https?://", href):
                el.attrib.update(rel="noopener noreferrer", target="_blank")


class VideoProcessor(BlockProcessor):
    RE = re.compile(r"^Video:\s*(?P<url>[\w.-]+)")

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m is None:
            # This should never happen, but just in case...
            logger.warn("We've got a problem video: %r" % block)
            return

        before = block[:m.start()]  # All lines before header
        after = block[m.end():]     # All lines after header
        if before:
            # As the header was not the first line of the block and the
            # lines before the header must be parsed first,
            # recursively parse this lines as a block.
            self.parser.parseBlocks(parent, [before])

        h = etree.SubElement(parent, "video")
        url = "{static}/static/" + m.group("url").strip()
        h.attrib.update(
            src=url,
            # TODO: These options should be configurable from the markdown content.
            muted="",
            playsinline="",
            preload="",
            controls="",
        )
        h.text = "Your browser does not support HTML5 video. Here's "
        a = etree.SubElement(h, "a", href=url)
        a.text = "a link to the video"
        a.tail = "instead."

        if after:
            # Insert remaining lines as first block for future parsing.
            blocks.insert(0, after)


class PrestigeDocsExt(Extension):
    def extendMarkdown(self, md):
        # Ref: <https://python-markdown.github.io/extensions/api/>.
        md.preprocessors.register(ImageLinks(md), "img_links", 200)
        md.preprocessors.register(FenceConfigs(md), "fence_configs", 200)
        md.treeprocessors.register(ExternalLinks(md), "ext_links", 20)
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~(.+?)~~", "del"), "del", 175)
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()\(\((.+?)\)\)", "kbd"), "kbd", 175)
        md.parser.blockprocessors.register(VideoProcessor(md.parser), "video", 175)


# This function will be called by python-markdown to get an instance of the extension.
def makeExtension(**kwargs):
    return PrestigeDocsExt(**kwargs)
