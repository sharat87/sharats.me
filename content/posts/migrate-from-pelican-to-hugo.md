---
title: "Migrate From Pelican to Hugo"
date: 2017-08-23T18:23:21+05:30
draft: true
---

I recently got around to resurrecting my blog up after around five years of death. As part of that,
I chose to migrate my blog to Hugo, from the current Pelican builder. The first post after
resurrection will be about the migration.

## A new site

Issued the command `hugo new site sharats.me`.

## Change metadata format

The article metadata in my Pelican site looks like the following:

```yaml
Title: Serializing python-requests' Session objects for fun and profit
Date: 18.2.2012
Tags: python, python-requests, python-pickle
Reddit: true
```

There's a lot of things in this that I wouldn't do if I wrote that article today, but meh. I need
this to look like the following to make Hugo happy.

```yaml
---
title: Serializing python-requests' Session objects for fun and profit
date: 2012-02-18
tags: ['python', 'python-requests', 'python-pickle']
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

