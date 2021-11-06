---
title: Migrate from Pelican to Hugo
tags: hugo, meta, awk, python
description: >
    A writeup on my experience migrating this blog website from Pelican to Hugo.
disqus_id: cache/posts/2017-08-23_migrate-from-pelican-to-hugo.html
---

**Update:** I have now moved to using a self-made Python program that compiles my markdown article
documents into the website you see. I'm keeping this article as a journal of my then experience.
{: .note }

I recently got around to resurrecting my blog up after around five years of death. As part of that,
I chose to migrate my blog to Hugo, from the current Pelican builder. The first post after
resurrection will be about the migration.

If you're wondering why the long break, well, I could blame it on life and work, but it was just me
being lazy. Hopefully, that won't happen again.

## Why Hugo

When I decided to start writing again, I couldn't remember who I was building the site. That's
probably entirely my fault for not documenting it for myself, but I ended up being almost new to
Pelican. So, instead of directly going to Pelican's homepage, I checked out
[StaticGen](https://www.staticgen.com/) to see the current landscape of static site generators. The
most popular (measure by GitHub stars) is obvious, Jekyll. Then came [Hugo](https://gohugo.io), a
name I didn't recognize. Other than Pelican, all the ones in the top-ten are built on Ruby or
JavaScript (node.js). I wasn't keen on either. Hugo was in a unique position since it is written in
a compiled language, so multiplatform binaries are relatively easy to come by.

I read the documentation on a weekend and I was impressed. Hugo it is. The thing that struck me most
in Hugo is that it does it's primary thing only. Generating HTML files from Markdown files. It
doesn't force a blog-like website or a documentation-like website. That's up to you. Hugo is like a
bridge between your markdown files and the output HTML files. The structure of the output is a
mirror image of your source files and the `config.toml` file (or `config.yaml`).

## Migration

### A new site

Issued the command `hugo new site sharats.me`.

### Configuration

Hugo's default configuration is of the [TOML](https://github.com/toml-lang/toml) format. I read the
README and wasn't convinced. Thankfully, Hugo supports configuration in [YAML](http://yaml.org/).

So, this is what I came up with in my `config.yaml` file.

```yaml
baseURL: http://sharats.me/
languageCode: en-us
title: "The Sharat's"
```

The current `config.yaml` is much longer and can be viewed on the github repo of this site.

### Change metadata format

The article metadata in my Pelican site looks like the following:

```yaml
Title: Serializing python-requests' Session objects for fun and profit
Date: 18.2.2012
Tags: python, python-requests, python-pickle
Reddit: true
```

There's a lot of things in this that I wouldn't do if I wrote that article today, but meh.

Hugo calls these *frontmatter* and I needed it to look like the following to make it happy.

```yaml
---
title: Serializing python-requests' Session objects for fun and profit
date: 2012-02-18
tags: 'python', 'python-requests', 'python-pickle'
reddit: true
---
```

The following `awk` script did the trick:

```awk
BEGIN { FS = ":"; OFS = ":"; print "---" }

!c && /^$/ { print "---\n"; c = 1 }

c { print; next }

!c {
    $1 = tolower($1)

    if ($1 == "date") {
        $2 = gensub(/ ([^.]+)\.([^.]+).([^.]+)/, " \\3-\\2-\\1", 1, $2)
        $2 = gensub(/-([0-9])-/, "-0\\1-", 1, $2)
    }

    if ($1 == "tags")
        $2 = " [" gensub(/[-a-z]+/, "'\\0'", "g", substr($2, 2)) "]"

    print
}
```

### Change code blocks

All my code blocks were of the following format:

        :::python
        import this

But, I needed them like this:

    ```python
    import this
    ```

So, the following little python script did the trick:

```python {"linenos": true}
#!/usr/bin/env python3

import sys


def process(f):
    cb = False
    empties = 0
    output = []
    for line in f:
        line = line.rstrip('\n')

        if not line:
            empties += 1
            continue

        prefix = ''
        if line.startswith('    '):
            line = line[4:]
            if not cb:
                cb = True
                line = line.replace(':::', '```', 1) if line.startswith(':::') else ('```\n' + line)

        elif cb:
            cb = False
            prefix = '```\n'

        output.append(prefix + '\n' * empties + line)
        empties = 0

    return '\n'.join(output)


for file_name in sys.argv[1:]:
    with open(file_name) as f:
        output = process(f)
    print(output)
```

Yeah, didn't have the patience to do it with `awk` this time.

## The Theme

I tried the themes over at the [Hugo themes page](http://themes.gohugo.io/), but just as I thought,
none of them were to my liking. I found the **nofancy** theme to be easy to get started and modify
to what I want, so that's what happened. Hugo's documentation is very good. I have to say, the
documentation is one of the reasons I'm loving Hugo.

Hope to be writing more articles in the coming weeks.
