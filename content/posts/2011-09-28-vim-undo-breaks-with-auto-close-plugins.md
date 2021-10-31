---
title: Vim undo breaks with auto-close plugins
tags: vim, vim-plugins
---

## Prelude

If you've used IDEs or other heavy editors ever in your life, you'd know how
nice it is to have parentheses and brackets to get auto-closed. If you don't
know what I'm talking about, its a feature usually present in IDEs like eclipse
and easily recreated in vim with mappings like

```vim
inoremap ( ()<Left>
```

Of course, that's just a simple taste. There are vastly complicated plugins that
achieve this.

Now, what's really super annoying about these plugins is that they tend to
break vim's amazingly powerful undo functionality. In other words, if you are
using an auto-close plugin, chances are, you can't rely on vim's undo anymore.

Debugging this and finding the cause has been on my todo list for quite some
time and a few days ago, I finally sat down to explore. I am writing my
experience here. First, a simple test case to see if the auto-close plugin you
use breaks undo, open vim (a blank file) and hit the following keys:

```vim
iabc{<CR><ESC>u
```

Where instead of `<CR>` you'd hit the return key and instead of `<ESC>` you'd
hit the Escape key. Decent knowledge of vim should tell you that after the above
keys, you should end up with a blank file again. Right?

If instead, you see a closing brace dangling in the second line, your undo is
broken. MUHAHAHAHAHA! You can't rely on undo anymore until you get rid of that
one plugin!

## What's going on?

So, experimenting with many auto-close plugins and reading the source of at
least 3 of those, I say there are basically two different implementations of
this functionality, which all these plugins use. The first one is pretty much
what was shown at the start of this article,

```vim
inoremap ( ()<Left>
" or
inoremap ( <C-r>="()\<Left>"
```

I'm going to call this class of plugins, the critters. These do *not* break your
undo. The next class of implementations, that do break your undo, the beasts, do
a bit of dark sorcery with stuff like

```vim
inoremap ( <C-r>=MyAwesomePairInseter()<CR>
```

There is no dark sorcery here that is immediately apparent. The real sorcery is
*inside* that function, where a call to `setline()` function is made to replace
your current line to contain the parentheses text at the cursor. Doesn't make
sense?  Don't worry, you'll get it soon enough.

## Which plugins? Name them!

Here are a few ones that break undo:

### Beasts

- <https://github.com/vim-scripts/AutoClose>
- <https://github.com/Raimondi/delimitMate>
- <https://github.com/Townk/vim-autoclose>

and these don't break undo

### Critters

- <https://github.com/vim-scripts/ClosePairs>
- <https://github.com/vim-scripts/simple-pairs>
- <https://github.com/vim-scripts/Auto-Pairs>

An initial look at them and you can tell, the ones that break undo are actually
more popular and have a relatively larger code base. So why doesn't anyone
complain about breaking undo?  I think they do and I believe the root cause is
a bug with *vim* itself.

The main difference in usability among these classes is again to do with undo.
In the beasts, typing a brace does not start a new undo action, but it does in
the critters (like hitting a `<C-g>u`). This might actually be playing a role in
why undo breaks in beasts only, but the exact reason escapes me.

## A reproducible test case

I wanted to reproduce this problem with a vanilla vim with no custom
configuration (except for `nocompatible`). So, I checked out the latest version
(vim73-353) from the mercurial repository, compiled (with python, ruby and
usual shit) and opened it, with no plugins and a simple vimrc as the following:

```vim
set nocompatible

inoremap <buffer> <silent> ( <C-R>=<SID>InsertPair("(", ")")<CR>
inoremap <buffer> <silent> [ <C-R>=<SID>InsertPair("[", "]")<CR>
inoremap <buffer> <silent> { <C-R>=<SID>InsertPair("{", "}")<CR>

function! s:InsertPair(opener, closer)
    let l:save_ve = &ve
    set ve=all

    call s:InsertStringAtCursor(a:closer)

    exec "set ve=" . l:save_ve
    return a:opener
endfunction

function! s:InsertStringAtCursor(str)
    let l:line = getline('.')
    let l:column = col('.')-2

    if l:column < 0
        call setline('.', a:str . l:line)
    else
        call setline('.', l:line[:l:column] . a:str . l:line[l:column+1:])
    endif
endfunction
```

Which is a stripped down version of the auto-close functionality implemented in
townk's auto-close plugin. And opened vim

```bash
vim -u undo-breaker-vimrc
```

and did the test here. Boom, a dangling brace character.

For all I know, its the call to `setline()` that's making all the difference.
But I could be entirely wrong with that. I say this because that is the major
difference between the two classes of implementations.

## Next?

I use persistent-undo in vim73 and heavily depend on it. Combined with the
[gundo][1] plugin by [Steve Losh][2], I get a kind of nicely visualized version
history that is centric to every file, which is quite handy in its own right.

[1]: http://sjl.bitbucket.org/gundo.vim
[2]: http://stevelosh.com

So, if there are others who have faced this, have a fix for it, perhaps a patch
to vim, or if there is already a bug in vim's bug database on this, let me know.

Thank you for reading.