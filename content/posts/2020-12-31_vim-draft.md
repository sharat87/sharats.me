---
title: Automating the ViM workplace
tags: [python, vim]
publish: no
---

I majorly use two tools for my coding workflow and one of them is GViM (on Windows). It's my primary
choice for editing text for ten years now and in that time, I've picked up several habits and tricks
that made me very productive. I'm hoping to do several articles in the coming weeks to share some of
these.

[TOC]

## Motivation

Most of my text editing involves working with Python, Markdown,
and JavaScript source files. When I'm spending as much time as I am with ViM, it ceases to be just a
tool in my mind. It becomes a state of mind where I'm able to translate my thoughts into actions much
faster than it/I can do with something else. It becomes my workplace.

Just like organizing one's desk or toolbox for maximum efficiency, treating ViM this way can help us
do something similar with our ViM. For that reason, I try to notice things that I do often, that
take more than 3-4 seconds of thought and then a few more seconds of hitting hotkeys or commands.
These are the ones I try to create a command or a hotkey. In my world, this is borderline
automation.

Note that what I'm sharing here is stuff I created/scavenged from years out of identifying patterns
*very specific* to my work style. My goal is not to share nice tidbits of ViM configuration. It is
to encourage you to identify your work style and work towards optimising it, before you go find a
plugin and *learn* the plugin's work style. Your own style of working deserves the first chance, and
not just in ViM.

Please note that all that I share below is what I'm using with ViM. I don't use NeoVim (yet) and I
can't speak for any of the below for NeoVim.

### Switching to normal mode

Probably the action that is done most often is switching to normal & insert modes. Switching to
insert mode is usually with several different keys (`i`, `a`, `o` etc.), but for switching to normal
mode, we usually use one single key. My preference for this is `<C-l>`, since `l` is on the home row
and the help pages already sort-of indicate that hitting it would go to the normal mode (if
`'insertmode'` is set, but well, it's unused otherwise). See `:h i_CTRL-l`.

```vim
nnoremap <C-l> <Esc>
```

Of course, now we need a quick way to open our vimrc file so we can add this mapping and then get
back to whatever we are doing. Well,

```vim
nnoremap cv :e $USERPROFILE/vimfiles/vimrc<CR>
```

The `cv` is a mnemonic for `change-vimrc`.

This is what I'm talking about when I say identify things that you often do. Even if you don't sit
down to automate it right away, put it on a sticky near your desk. Spend a few minutes thinking
about it. A few seconds in a time of intense focus is far more dear than a few minutes in slacking.

### Start GViM maximized, in Windows

As another example, I wanted GViM to start maximized when I open it. On way to do this was to check
the Maximized checkbox in the GViM shortcut's properties. But that won't work when I start GViM from
a command line. The solution that worked even better:

```vim
" Maximize gVim window.
if exists(':simalt') > 0 && s:iswin
  autocmd ssk GUIEnter * simalt ~x
endif
```

### Save all buffers

I often use the `:wa` command to save all my open buffers. But it has the nasty habit of throwing an
error when it's not able to save all buffers. This is annoying because I often have scratch buffers
in vertical splits where I dump random pieces of copied text and thoughts. So, I prepared the
following hotkey that will execute the `:wa` command and, if that error comes up, shows a message
instead.

```vim
nnoremap <silent> <C-m> :try\|wa\|catch /\<E141\>/\|echomsg 'Not all files saved!'\|endtry<CR>
```

This doesn't look like an ideal solution, but it hasn't failed me yet. The idea is not to create an
perfect solution, but just one that works well with you.

### Copy to system clipboard

I often have to copy stuff to system clipboard to paste into chat channels and emails. The standard
way to do this would be something like `"+yap` in normal mode, or `"+y` in visual mode. This is
annoying, not because it's three keys, but more because they are hard to type in order and they are
all with the same hand. So I solved it with the following keys:

```vim
xnoremap <C-c> "+y
nnoremap <silent> cp "+y
nnoremap <silent> cpp "+yy
```

With this, `<C-c>` in visual mode copies to clipboard and `cp` can be used with text objects. Much
easier to hit.


## Ensure directory of file exists, before saving

I often edit new files like `:e css/styles.css`, without realizing that I have to create the `css`
folder before saving this. But that's not productive, my tool should do that automatically.

```vim
" Create file's directory before saving, if it doesn't exist.
" Original: https://stackoverflow.com/a/4294176/151048
augroup BWCCreateDir
  autocmd!
  autocmd BufWritePre * :call s:MkNonExDir(expand('<afile>'), +expand('<abuf>'))
augroup END
fun! s:MkNonExDir(file, buf)
  if empty(getbufvar(a:buf, '&buftype')) && a:file !~# '\v^\w+\:\/'
    call mkdir(fnamemodify(a:file, ':h'), 'p')
  endif
endfun
```

Let's see what's going on here. Firstly, we define an `autocmd` for the `BufWritePre` event, which
is fired just before a file is saved, to call the function `s:MkNonExDir`. In this function, we
check for the buffer being a normal buffer (see `:h buftype`) and if it is, create it's parent
directory. Simple, non-intrusive, and effective.

TODO: After scripts.

TODO: Notes plugin.

TODO: Using the Python API.






## Conclusion

I also encourage you to go over the ViM help pages often. They contain some awesome tips and ideas
that serve as great starter points to improve your workflow.

Identify, optimize, repeat.

When you're not doing that, grab a coffee and browse the ViM help pages!
