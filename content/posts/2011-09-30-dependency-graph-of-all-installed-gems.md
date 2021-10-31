---
title: Dependency graph of all installed gems
tags: ruby, gem, graphviz, bash, tips
---


Every other application written using ruby these days seem to come with this
installation instruction:

    gem install my-super-awesome-app

and then going on to describing how awesome the app is. But, installing the app
in the above way installs all its bazillion dependencies, which, unfortunately
are not uninstalled when you uninstall this app with

    gem uninstall the-same-damn-app

And so, you have huge mess of gems installed which you have no idea why they
are there in the first place. Finding out stale gems that are left out because
of this can be a pain.

So, I decided a neat flowchart visualising the dependency relationships between
all the installed jars would give me a picture. And yes, it did.

![Gem dependency graph](/img/gem-dependency-graph.png)

Here's how I got the flowchart: (save this in say, gem-graph.sh)

```bash
#!/bin/bash

gem list \
    | cut -d\  -f1 \
    | xargs gem dep \
    | awk '\
        BEGIN { print "digraph gems {" } \
        /^Gem / { cur=$2; sub(/-[0-9\.]+$/, "", cur); print "  \"" cur "\";" } \
        ! /^Gem / && $0 != "" { print "  \"" cur "\" -> \"" $1 "\";" } \
        END { print "}" }' \
    | dot -Tpng -o gems.png
```

Assuming you have [GraphViz](http://www.graphviz.org/) installed, you can just
do

    chmod +x gem-graph.sh
    ./gem-graph.sh

and the graph will be saved in gems.png. Happy gem cleaning :).