---
title: Automating the Vim workplace
tags: [vim, productivity]
desc: >
    Learn to identify actions in your Vim workflow and automate them, and improve your productivity!
---

I majorly use two tools for my coding workflow and one of them is GVim (on Windows). It's my primary
choice for editing text for ten years now and in that time, I've picked up several habits and tricks
that made me very productive. I'm hoping to do several articles in the coming weeks to share some of
these.

[TOC]

## Motivation

Most of my text editing involves working with Python, Markdown, and JavaScript source files. When
I'm spending as much time as I am with Vim, it ceases to be just a tool in my mind. It becomes a
state of mind where I'm able to translate my thoughts into actions much faster than it/I can do with
something else (besides being an excuse to be fancy with words). It becomes my workplace.

Just like organizing one's desk or toolbox for maximum efficiency, we can mold Vim to help us
achieve something similar with it. I try to notice things that I do often, that take more than 3-4
seconds of thought and then a few more seconds of hitting hotkeys or commands. These are the ones I
try to create a command or a mapping. In my world, this is borderline automation.

What I'm sharing here is stuff I created/scavenged through years of identifying patterns *very
specific* to my work style. My goal is not to share nice tidbits of Vim configuration. It is to
encourage you to identify your work style and work towards optimising it, before you go find a
plugin and *learn* the plugin's work style. As such, I don't expect you to resonate with the tips I
shared here. Your own style of working deserves the first chance, let Vim learn it.

Side note: that all that I share below is what I'm using with Vim. I don't use NeoVim (yet) and I
can't speak for any of the below for NeoVim.

## Switching to Normal Mode

Probably the action that is done most often is switching to normal & insert modes. Switching to
insert mode is usually with several different keys (`i`, `a`, `o` etc.), but for switching to normal
mode, we usually use one single key. My preference for this is `<C-l>`, since `l` is on the home row
and the help pages already sort-of indicate that hitting it would go to the normal mode (if
`'insertmode'` is set, but well, it's unused otherwise, See `:h i_CTRL-l`).

    :::vim
    inoremap <C-l> <Esc>

This is a topic that often brings up an uncontrollable urge to be vocal about one's own choice of
keys to go to normal mode. I've used several of them over the years, `jj`, `<CapsLock>` as `<ESC>`,
`<C-[>`, `<C-c>`, mapping `<C-k>`, *xcape* in the background, etc. All of them felt haphazard, and
`<C-l>` worked the best for me. As I said, this article is about what worked best to *my* workflow.
Go discover your own.
{: .note }

Of course, now we need a quick way to open our `vimrc` file so we can add this mapping and then get
back to whatever we are doing. Well,

    :::vim
    nnoremap cv :e $MYVIMRC<CR>

The `cv` is a mnemonic for *change vimrc*.

> This mapping was originally defined as `:e $USERPROFILE/vimfiles/vimrc<CR>`. Thanks to the helpful
> community at [r/vim][] and a comment here, I realized `$MYVIMRC` is a better fit here. Thank you
> folks!

[r/vim]: https://www.reddit.com/r/vim/comments/enlz8x/automating_the_vim_workplace/fe396x0

This is what I'm talking about when I say identify things that you often do. Even if you don't sit
down to automate it right away, put it on a sticky near your desk. Spend a few minutes thinking
about it. A few seconds in a time of intense focus is far more dear than a few minutes in slacking.

Note that this mapping is not without it's quirks. It interferes with the line completion mapping,
`<C-x><C-l>`. It'll still work, but right after triggering `<C-x><C-l>`, if you hit `<C-l>`, you
won't go to normal mode. You'll merely go to the next selected item in the completion popup. Other
than this, `<C-l>` for going to normal mode works quite well.

Now that the mapping is setup, I can hit `<C-l>` in insert mode to go to normal mode. Then I noticed
something else in the way I *tried* to use it, subconsciously. I started hitting `<C-l>` in visual
mode, operator pending mode etc. to go into normal mode. I realized I was using `<C-l>` essentially
as a replacement of `<ESC>`. But of course it failed because I only created a mapping for insert
mode.

After a few iterations and shower thoughts, this is what I currently use:

    :::vim
    " Easier way to go to normal mode. Also, alternative to <ESC>.
    noremap! <silent> <C-l> <ESC>
    vnoremap <silent> <C-l> <ESC>
    onoremap <silent> <C-l> <ESC>

I also wanted this from the command line, but I'm still trying to get it to work. I currently have
the following but it's not very robust. Every time I hit `<C-l>` in the normal mode, the cursor
moves ahead by two characters. Still working on getting it to work well.

    :::vim
    cnoremap <silent> <C-l> <C-c>  " <ESC> doesn't work and even this moves the cursor by two characters.

It's a never ending process of learning and experimenting.

## Start GVim Maximized, in Windows

As another example, I wanted GVim to start maximized when I open it. On way to do this was to check
the Maximized checkbox in the GVim shortcut's properties. But that won't work when I start GVim from
a command line. The solution that worked even better:

    :::vim
    " Maximize gVim window.
    let s:iswin = has('win32') || has('win64')
    if exists(':simalt') > 0 && s:iswin
      autocmd GUIEnter * simalt ~x
    endif

## Save All Buffers

I often use the `:wa` command to save all my open buffers. But it has the nasty habit of throwing an
error when it's not able to save all buffers. This is annoying because I often have scratch buffers
in vertical splits where I dump random pieces of copied text and thoughts. So, I prepared the
following hotkey that will execute the `:wa` command and, if that error comes up, shows a message
instead.

    :::vim
    nnoremap <silent> <C-m> :try\|wa\|catch /\<E141\>/\|echomsg 'Not all files saved!'\|endtry<CR>

This doesn't look like an ideal solution, but it hasn't failed me yet. The idea is not to create an
perfect solution, but just one that works well with you.

If you're using the above mapping, note that mapping to `<C-m>` is almost the same as mapping to the
`Return` key on your keyboard. So hitting the return key in normal mode will also trigger the above
mapping. Just something to keep in mind.
{: .note }

## Copy to System Clipboard

I often have to copy stuff to system clipboard to paste into chat channels and emails. The standard
way to do this would be something like `"+yap` in normal mode, or `"+y` in visual mode. This is
annoying, not because it's three keys, but more because they are hard to type in order and they are
(almost) all with the same hand. So I solved it with the following keys:

    :::vim
    xnoremap <C-c> "+y
    nnoremap <silent> cp "+y
    nnoremap <silent> cpp "+yy

With this, `<C-c>` in visual mode copies selection to clipboard and `cp` can be used with text
objects. Much easier to hit.

## Ensure Directory Exists, Before Saving

I often edit new files like `:e css/styles.css`, without realizing that I have to create the `css`
folder before saving this. But that's not productive, my tool should do that automatically.

    :::vim {linenos: yes}
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

Let's see what's going on here. Firstly, we define an `autocmd` for the `BufWritePre` event, which
is fired just before a file is saved, to call the function `s:MkNonExDir`. In this function, we
check for the buffer being a normal buffer (see `:h buftype`) and if it is, create it's parent
directory.

Simple, non-intrusive, and effective.

## Switching to Alternate Buffer

The default key-binding for `<C-^>` (or `<C-6>`, `:h CTRL-6`) lets us quickly switch back-and-forth
between two buffers. This is extremely handy and is likely one of my most used functionality for
switching buffers within Vim.

There's some annoying quirks to this mapping though. For example, if there's files in your buffer
list, but no *alternate* buffer, we'll get an error saying "No alternate buffer". Which is not
helpful. So a few years ago I saw a mapping to go to the next buffer if there's no alternate buffer.
It worked to an extent, but there's more.

When I delete a buffer with `:bd`, I get taken to a different buffer. Now if I hit `<C-6>` again,
the buffer I just deleted is loaded again and I'm back in it. This may be what one usually wants,
but for me, I want to be taken to the next buffer that's still *loaded*, not deleted ones.

    :::vim
    " My remapping of <C-^>. If there is no alternate file, and there's no count given, then switch
    " to next file. We use `bufloaded` to check for alternate buffer presence. This will ignore
    " deleted buffers, as intended. To get default behaviour, use `bufexists` in it's place.
    nnoremap <silent> <C-n> :<C-u>exe v:count ? v:count . 'b' : 'b' . (bufloaded(0) ? '#' : 'n')<CR>

This is the mapping I use for switching between alternate buffers. I use `<C-n>` as it's easier to
hit and there's a simpler key for it's default functionality anyway (`j`).

Additionally if you're using the [eunuch plugin](https://github.com/tpope/vim-eunuch/), this
mapping will not navigate to a buffer that's been `Delete`-ed.

## Run Git Commands in `:terminal`

Running git commands is another thing I often do, while working in Vim. Most of the time, it just a
`status` or `diff`, so I needed something quicker than switching to a terminal and running the
command.

I initially used [fugitive][], but it felt slow on Windows (very likely because of the required
anti-virus). It works fine when I'm on Linux, but on Windows, it's not productive for me. Besides,
it does a lot of things I don't usually need. The following is the mapping that serves *most* of
what I need from within Vim.

[fugitive]: https://github.com/tpope/vim-fugitive

    :::vim
    nnoremap <Leader>g :ter git --no-pager<Space>

So, what does this do? Well, I hit `,g` (because `,` is my `mapleader`) and the cursor is placed in
the command line with the following pre-filled:

    :::vim
    :ter git --no-pager

Then I just hit `st<Enter>`, which will open a new terminal within Vim which runs `git st` command
asynchronously (which is an alias to `git status`).

After seeing the output I noticed that I immediately issued another `,gdiff<Enter>`, which opens up
another terminal split to run the `git diff` command. Such multiple splits quickly got annoying
again. Yeah, I'm easily annoyed. I need this mapping to *not* open a new split if I'm already in a
`git` output terminal window. Here's what I'm using currently:

    :::vim
    nnoremap <Leader>g :ter <C-r>=&buftype == 'terminal' && job_info(term_getjob('%')).cmd[0] ==? 'git' ? '++curwin ' : ''
                \ <CR>git --no-pager<Space>

We check if the current buffer is a terminal and if the command is `git`, if yes, we tell `:ter` to
open the terminal in the current window instead of opening up a new split.

## Non-undo-able Insert Mode Commands

In insert mode, `<C-u>` deletes everything from start of current line to cursor position (this is
not *exactly* true, read `:h i_CTRL-U` for the exact behaviour, I won't repeat it here). This is
quite convenient and I use it a lot more than I like to admit. Often, when I start a statement in a
new line, I have second thoughts middle of the line and I quickly hit `<C-u>` and start typing in
the idea from my second thought. But then of course, I realize that what I was doing originally was
the right way. Now if I try to undo what's done by `<C-u>`, I can't. Since it's all treated as one
insert operation, it's all one undo step.

This is why I got this:

    :::vim
    " CTRL-U in insert mode deletes a lot. Put an undo-point before it.
    inoremap <C-u> <C-g>u<C-u>

I don't recall the source of this but I found this after a bit of searching online for a solution
and it works! Whoever came up with this, thank you!

> Thanks to this [kind person's
> hint](https://www.reddit.com/r/vim/comments/enlz8x/automating_the_vim_workplace/fe3973i), I was
> able to find the source of this. It's actually in the `defaults.vim` file that is shipped with
> Vim.

## Quickly Open `ftplugin`

This is one that I don't use *as often* as some of the above, but when I do need it, it's extremely
handy. I use the `$VIMFILES/after/ftplugin` directory to put in my custom settings for specific file
types. These files usually don't just contain changes in settings like indentation, but also
`commentstring` and often some command that makes editing that specific `filetype` a bit easier.

These commands let me open the plugin file in that directory for the `filetype` I'm currently
working with.

    :::vim
    " Edit my filetype/syntax plugin files for current filetype.
    command -nargs=? -complete=filetype EditFileTypePlugin
                \ exe 'keepj vsplit $VIMFILES/after/ftplugin/' . (empty(<q-args>) ? &filetype : <q-args>) . '.vim'
    command -nargs=? -complete=filetype Eft EditFileTypePlugin <args>

The same thing for syntax plugin:

    :::vim
    command -nargs=? -complete=filetype EditSyntaxPlugin
                \ exe 'keepj vsplit $VIMFILES/after/syntax/' . (empty(<q-args>) ? &filetype : <q-args>) . '.vim'
    command -nargs=? -complete=filetype Esy EditSyntaxPlugin <args>

These commands are obviously heavily inspired by the `:EditUltiSnipsFile` command from the
[UltiSnips][] plugin (which is great at automation by the way).

[UltiSnips]: https://github.com/sirver/UltiSnips

## Sorting over Motion

Vim comes with the `:sort` command that sorts the range of lines provided. So, for example, to sort
the whole file, we'd do `:%sort`. To sort the first ten lines, something like `:1,10sort` should do.
The range of lines given will be replaced with the sorted lines.

This is convenient, but not very handy. But I'd always wanted a way to sort over a motion, like
*sort this paragraph* or *sort inside braces* etc. So, after some searching online and digging the
Vim documentation, I have the following in my `vimrc`:

    :::vim
    " Sort lines, selected or over motion.
    xnoremap <silent> gs :sort i<CR>
    nnoremap <silent> gs :set opfunc=SortLines<CR>g@
    fun! SortLines(type) abort
        '[,']sort i
    endfun

With this, hitting `gsip` would sort the lines *inside* the current paragraph. Similarly, `gsiB`
would sort lines inside the braces closest to the cursor (try this one in CSS!). If you have the
[vim-indent-object](https://github.com/michaeljsmith/vim-indent-object/) plugin, you could also do
`gsii` to sort lines in current indent block.

Additionally, we also have an `xnoremap` mapping definition which lets us use `gs` in visual mode to
sort the highlighted lines. I don't use this as often as the operator version above, but it's nice
to have nonetheless.

## Reversing over Motion

This is very similar to the above. Instead of sorting, I'm reversing the lines. Unfortunately, we
don't have a `:reverse` command like `:sort`, so this one is more DIY.

    :::vim {linenos: yes}
    " Reverse lines, selected or over motion.
    nnoremap <silent> gr :set opfunc=ReverseLines<CR>g@
    vnoremap <silent> gr :<C-u>call ReverseLines('vis')<CR>
    fun! ReverseLines(type) abort
        let marks = a:type ==? 'vis' ? '<>' : '[]'
        let [_, l1, c1, _] = getpos("'" . marks[0])
        let [_, l2, c2, _] = getpos("'" . marks[1])
        if l1 == l2
            return
        endif
        for line in getline(l1, l2)
            call setline(l2, line)
            let l2 -= 1
        endfor
    endfun

I mapped reversing to `gr`, which works similar to the `gs` from previous section, but instead of
sorting, the lines will be reversed. Everything in the above snippet can be looked up with `:h`
command within Vim. I'll leave the understanding-it's-working part as an exercise to the reader, if
inclined.

## Conclusion

This articles looks an awful lot like a list of Vim tips, but I implore you to see further. I picked
these specific things from my Vim setup (which is a lot bigger than this) to illustrate the idea of
identifying and then automating. Of course, these snippets I shared above, in my opinion are too
small for a full blown plugin, yet not too insignificant to not be shared. I intend to follow up
with more ideas from my configuration, so stay tuned.

I also encourage you to go over the Vim help pages often. They contain some awesome tips and ideas
that serve as great starter points to improve your workflow. So, just, you know, while that really
long build is running, grab a coffee and open the Vim docs!

Identify, optimize, repeat.
