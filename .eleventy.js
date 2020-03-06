const { DateTime } = require("luxon");
const fs = require("fs");
const pluginRss = require("@11ty/eleventy-plugin-rss");
const pluginNavigation = require("@11ty/eleventy-navigation");
const markdownIt = require("markdown-it");
const cheerio = require("cheerio");
const {unescapeAll, escapeHtml} = require("markdown-it/lib/common/utils");
const DEV_MODE = require("./_data/DEV_MODE");

module.exports = function (eleventyConfig) {
	eleventyConfig.addPlugin(pluginRss);

	setupSyntaxHighlighting(eleventyConfig);

	eleventyConfig.addPlugin(pluginNavigation);

	eleventyConfig.setDataDeepMerge(true);

	eleventyConfig.addLayoutAlias("post", "layouts/post.njk");

	eleventyConfig.addFilter("readableDate", date => DateTime.fromJSDate(date).toFormat("d LLL yyyy"));

	eleventyConfig.addFilter("monthLabel", date => DateTime.fromJSDate(date).toFormat("LLLL yyyy"));

	// https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#valid-date-string
	eleventyConfig.addFilter("iso", dateObj => DateTime.fromJSDate(dateObj).toFormat("yyyy-LL-dd"));

	// Get the first `n` elements of a collection.
	eleventyConfig.addFilter("head", (array, n) => {
		if( n < 0 ) {
			return array.slice(n);
		}

		return array.slice(0, n);
	});

	eleventyConfig.addCollection("tagList", require("./_11ty/getTagList"));

	// FIXME: Future articles are being generated, and are part of `collections.all` and so are in sitemap.
	eleventyConfig.addCollection("posts", collection => {
		let posts = collection.getFilteredByGlob("posts/*");
		if (!DEV_MODE) {
			const now = new Date();
			posts = posts.filter(p => p.date && p.date <= now);
		}
		return posts;
	});

	eleventyConfig.addPassthroughCopy("img");
	eleventyConfig.addPassthroughCopy("css");
	eleventyConfig.addPassthroughCopy("js");
	eleventyConfig.addPassthroughCopy({"static/**/*": "."});

	const markdownLibrary = makeMarkdownRenderer();
	eleventyConfig.setLibrary("md", markdownLibrary);

	eleventyConfig.addFilter("markdown", (content) => {
		const html = markdownLibrary.render(content);
		return html.substr(3, html.length - 8);
	});

	eleventyConfig.addTransform("htmlPostProcessor", (content, outputPath) => {
		if (!outputPath.endsWith(".html"))
			return content;

		const $ = cheerio.load(content);
		transformFinalHTML($);

		return $.root().html();
		// Typeset disabled because of <https://github.com/davidmerfield/Typeset/issues/62>
		// return require("typeset")($.root().html(), {
		// 	disable: ["hyphenate", "hangingPunctuation", "smallCaps"],
		// });
	});

	/*
	eleventyConfig.addLinter("inclusive-language", (content, inputPath, outputPath) => {
		const words = "simply,obviously,basically,of course,clearly,just,everyone knows,however,easy".split(",");
		if (inputPath.endsWith(".md")) {
			for (const word of words) {
				const regexp = new RegExp("\\b(" + word + ")\\b", "gi");
				if(content.match(regexp)) {
					console.warn(`Inclusive Language Linter (${inputPath}) Found: ${word}`);
				}
			}
		}
	});
	*/

	// Browsersync Overrides
	eleventyConfig.setBrowserSyncConfig({
		callbacks: {
			ready: function(err, browserSync) {
				const content_404 = fs.readFileSync('_site/404.html');

				browserSync.addMiddleware("*", (req, res) => {
					// Provides the 404 content without redirect.
					res.write(content_404);
					res.end();
				});
			},
		},
		ui: false,
		ghostMode: false
	});

	return {
		templateFormats: [
			"md",
			"njk",
			"html",
			"liquid"
		],

		// If your site lives in a different subdirectory, change this.
		// Leading or trailing slashes are all normalized away, so don’t worry about those.

		// If you don’t have a subdirectory, use "" or "/" (they do the same thing)
		// This is only used for link URLs (it does not affect your file structure)
		// Best paired with the `url` filter: https://www.11ty.io/docs/filters/url/

		// You can also pass this in on the command line using `--pathprefix`
		// pathPrefix: "/",

		markdownTemplateEngine: "njk",
		htmlTemplateEngine: "njk",
		dataTemplateEngine: "njk",

		// These are all optional, defaults are shown:
		dir: {
			input: ".",
			includes: "_includes",
			data: "_data",
			output: "_site"
		}
	};
};


function setupSyntaxHighlighting(eleventyConfig) {
	const pluginSyntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight");
	eleventyConfig.addPlugin(pluginSyntaxHighlight, {
		init: function ({ Prism }) {
			require("prismjs/components/")(["python", "shell-session", "bash", "autohotkey"]);
			Prism.languages.awk = Prism.languages.clike;
			Prism.languages.pycon = Prism.languages.python;
			Prism.languages.console = Prism.languages["shell-session"];
			Prism.languages.sh = Prism.languages.bash;
			Prism.languages.ahk = Prism.languages.autohotkey;
		}
	});
}


function makeMarkdownRenderer() {
	const md = markdownIt({
		html: true,
		linkify: true
	});

	md.use(require("markdown-it-anchor"), {
		permalink: true,
		slugify
	});

	md.use(require("markdown-it-table-of-contents"), {
		markerPattern: /^\[toc\]$/im,
		includeLevel: [2, 3],
		containerHeaderHtml: '<details class="toc"><summary>Table of Contents</summary>',
		containerFooterHtml: '</details>',
		slugify
	});

	md.use(require("markdown-it-attrs"), {
		leftDelimiter: '{:',
		rightDelimiter: '}'
	});

	md.use(require("markdown-it-deflist"));

	md.use(require("markdown-it-footnote"));

	md.use(require("markdown-it-sup"));

	md.use(require("markdown-it-abbr"));

	md.renderer.rules.fence_orig = md.renderer.rules.fence;
	md.renderer.rules.fence = codeFenceRenderer;

	// Table wrapping.
	md.renderer.rules.table_open = () => '<div class=table-wrapper><table>\n';
	md.renderer.rules.table_close = () => '</table></div>\n';

	return md;
}


function codeFenceRenderer(tokens, idx, options, env, slf) {
	let html = slf.rules.fence_orig(tokens, idx, options, env, slf);

	// Prism turns newline characters to `<br>`. Figure out how to get it to not to.
	html = html.replace(/<br>/g, "\n");

	const match = tokens[idx].info.match(/^(\w+)(\s+.+)?$/);
	if (!match)
		return html;

	const lang = match[1], extra = match[2];
	if (!extra)
		return html;

	const config = JSON.parse(extra);
	html = `<div class="hl" ${lang ? ('data-lang="' + lang + '"') : ""}>` + html + "</div>";
	let extraWrapping = false;

	if (config.linenos) {
		extraWrapping = true;
		const match = tokens[idx].content.match(/\n(?!$)/g);
		const linesNum = match ? match.length + 1 : 1;
		const nums = [];
		for (let i = 1; i <= linesNum;)
			nums.push(i++);
		const lineNosMarkup = "<div class=linenodiv aria-hidden=true><pre>" + nums.join("\n") + '</pre></div>'
		html = lineNosMarkup + html;
	}

	if (config.filename) {
		extraWrapping = true;
		const filename = config.filename.trim();
		const downloadLink = '<a href="data:text/plain,' + tokens[idx].content.replace(/"/g, '&quot;') + '" class="download-btn button" download="' + filename + '">Download</a>';
		html = "<span class=filename>" + filename + downloadLink + "</span>" + html;
	}

	if (extraWrapping)
		html = "<div class=hltable>" + html + "</div>";

	return html;
}


function slugify(text) {
	// Source: <https://github.com/Python-Markdown/markdown/blob/master/markdown/extensions/toc.py>
	return text.normalize("NFKD").replace(/[^\w\s]+/g, "")
		.trim().toLowerCase().replace(/[-\s]+/g, "-");
}


function transformFinalHTML($) {
	// Why `rel=noopener`? See <https://web.dev/external-anchors-use-rel-noopener/>.
	$("a[href^='https://']:not([href^='https://sharats.me'])").attr("rel", "noopener");

	// Tables need to be wrapped in a div so they can be horizontally scrolled on smaller screens.
	// $("table").wrap("<div>").parent().addClass("table-wrapper");

	// FIXME: Need a simpler faster way to do this, at the `markdown-it` level.
	$(".table-of-contents a").each((index, el) => {
		$(el).html($($(el).attr('href')).html());
	}).find('.header-anchor').remove();

	// Special class for paragraphs with just a single image.
	$("p > img, p > [role='img'], p > svg").each((index, el) => {
		const parent = $(el).parent()
		if (parent.children().length === 1)
			parent.addClass("just-image");
	});

	// Check TODO paragraphs.
	$("p, li").each((index, el) => {
		el = $(el);
		if (el.text().match(/^(TODO|FIXME|XXX):/)) {
			console.warn('Found TODO item:', el.text());
			el.css({background: "#FFA", color: "#C00", "font-weight": 600, "font-size": "1.3em"});
		}
	});

}
