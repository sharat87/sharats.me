---
title: A tasty vim configuration setup with Vimpire and Pathogen
tags: vim, vim-plugins, vimpire, pathogen
---


Managing vim plugins has always been a hassle. Until pathogen came along. If
you are using vim with quite a few vim plugins, then you should be using
pathogen, if you are not, you are seriously depriving yourself of sanity. No,
seriously. You should.

So, I assume you are also versioning your `.vim` directory, like on GitHub or
BitBucket with git or mercurial respectively. If you are not, then you should.
You really really should.

If your answer was no to both of the above, you better get the hell out of here
before I get my lawn mowers.

Okay, if you tried to version your `.vim` directory, but the plugin directories
inside pathogen's bundle directory are repositories themselves, you won't be
very happy. You either have to version all the .git and .hg and what not
version directories from the plugins, or you just have to ignore them all and
forgo versioning for individual plugins. But if you chose the latter, in which
case versioning your `.vim` will be easy, updating your plugins is a serious
pain.

So, recently, <http://vim-scripts.org> came up and so did scripts like vundle and
vim-update-bundles, as listed on the tools page on <http://vim-scripts.org>.
These let you list the plugins you use in your vimrc file and they take care of
keeping them up to date. The advantage is that you can version your `.vim`
directory, and wherever you clone it, you can just run the script used and all
your plugins are set up, the latest versions of them, just like that. Awesome!

Vimpire isn't much different from those tools. In fact, it is very similar to
vim-update-bundles in functionality, but there are 2 main differences. First
off, it is written in python. I won't spell out the implications of that. But,
it is ruby-less. Second, it supports hg. Yay! So, you can get plugins not just
from git, but also from hg.

How to set it up and how to use it can be seen on the BitBucket page, via the
README file.

Hosted at <http://bitbucket.org/sharat87/vimpire/src>

Please note that this is still beta. Tested on windows 7. I am waiting to get
back to Ubuntu, but until then, no idea if it works on unix like machines.

Update: The latest version works perfectly with Ubuntu too!
