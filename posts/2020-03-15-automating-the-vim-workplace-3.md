---
title: Automating the Vim workplace -- Chapter Ⅲ
tags: [vim, productivity]
description: >
    More ideas and inspiration for identifying repeated actions in your Vim workflow and automate
    them, and improve your productivity! A follow up to the previous article on this topic.
---

This is the third installment of my [Automate the Vim workplace][first-article] article series. As
always, feel free to grab the ideas in this article or, better yet, take inspiration and inspect
your workflow to identify such opportunities.

This chapter is all about messing around with text objects and motions. By that, I don't mean
creating custom text objects and custom cursor movements, there's enough of those already. Instead
I'm going to write about custom operations to apply on those text objects. I feel this part of the
subject doesn't get as much attention comparatively. Besides, I have more of those in my vimrc than
just custom text objects so that's what I'll write about.  Take this as inspiration to define your
own custom operations to do over your (custom?) text objects.

[TOC]

Please note that all that I share below is what I'm using with Vim (more specifically, GVim on
Windows). I don't use Neovim (yet) and I can't speak for any of the below for Neovim.
{: .note }

## Copy file full path

I work with CSV files quite a bit. I spend a lot of time grooming them, fixing them etc. in Vim and
then once it is ready, I need to upload it to an internal tool. For that, the following command has
proven to be super useful.

```vim
" Command to copy the current file's full absolute path.
command CopyFilePath let @+ = expand(s:iswin ? '%:p:gs?/?\\?' : '%:p')
```

This is one of those commands that feel super-simple and super-obvious once we add it to our
workflow. Running this command places the full path of the current buffer's file into the system
clipboard. Then, I just go to my browser, click on the upload button and paste the file location.
This is much quicker than having to navigate to the folder and selecting the file. It also helps
avoid selecting the wrong file (which happened more than once to me).

## Squeeze / Expand contiguous blank lines

When building or editing large CSV files, I often end up with several (read: hundreds) of blank
lines. This is usually because I select those lines in visual block mode, cut them, and then paste
as a new column to some existing rows. Solving that problem is for another day I suppose.

Nonetheless, I needed a quick way to condense all those blank lines into a single blank line. The
following is the result of that:

```vim
nnoremap <silent> dc :<C-u>call <SID>CleanupBlanks()<CR>
fun! s:CleanupBlanks() abort
    if !empty(getline('.'))
        return
    endif
    let l:curr = line('.')

    let l:start = l:curr
    while l:start > 1 && empty(getline(l:start - 1))
        let l:start -= 1
    endwhile

    let l:end = l:curr
    let l:last_line_num = line('$')
    while l:end < l:last_line_num && empty(getline(l:end + 1))
        let l:end += 1
    endwhile

    if l:end >= l:start + v:count1
        exe l:start . '+' . v:count1 . ',' . l:end . 'd_'
    else
        call append(l:end, repeat([''], v:count1 - (l:end - l:start) - 1))
    endif
    call cursor(l:start, 1)
endfun
```

This defines the <kbd>dc</kbd> mapping, which will condense multiple blank lines under the cursor
into a single one.

Then, on a weekend when I was feeling particularly silly, I extended this to take a range, a number
in front of <kbd>dc</kbd> which specifies the number of newlines to leave. So now, this mapping can
both condense, and expand vertical blank space to any size I want! Yay silly weekends!

## Duplicate Text in Motion

Copy-pasta is a legitimate writing and coding technique. But I do it so often, I started thinking of
*duplicating* as an operation different from *yanking*. But if that is so, *duplicating* some text
should not mess with my registers. So I built a mapping that would let me duplicate the text over
any motion (like text objects), without touching the registers. Following is how it's built:

```vim
" Duplicate text, selected or over motion.
nnoremap <silent> <Leader>uu :t.\|silent! call repeat#set('duu', v:count)<CR>
nnoremap <silent> <Leader>u :set opfunc=DuplicateText<CR>g@
vnoremap <silent> <Leader>u :<C-u>call DuplicateText('vis')<CR>
fun! DuplicateText(type) abort
    let marks = a:type ==? 'vis' ? '<>' : '[]'
    let [_, l1, c1, _] = getpos("'" . marks[0])
    let [_, l2, c2, _] = getpos("'" . marks[1])

    if l1 == l2
        let text = getline(l1)
        call setline(l1, text[:c2 - 1] . text[c1 - 1:c2] . text[c2 + 1:])
        call cursor(l2, c2 + 1)
        if a:type ==? 'vis'
            exe 'normal! v' . (c2 - c1) . 'l'
        endif

    else
        call append(l2, getline(l1, l2))
        call cursor(l2 + 1, c1)
        if a:type ==? 'vis'
            exe 'normal! V' . (l2 - l1) . 'j'
        endif

    endif
endfun
```

Now, what used to be <kbd>yap}p</kbd> has become <kbd>,uap</kbd>. That's just one key reduced but a
reduction in keys is not what I'm aiming at here. It's cognitive load of "duplicate this text" over
"copy this text, go to end of text, paste text". This works in visual mode as well, though I don't
use it as often.

As an added benefit, the duplicated text is selected in visual mode. This quickly visually
highlights for me the newly inserted text so I can get back on track as to what I intended to do
with the duplicated text.

## Transpose (using `:py3`)

This is another mapping I created to help me with CSV files. Specifically, this one works with
tab-separated files, which are even more awesome to edit in Vim with the [vartabstop][] option. The
next section describes how I use this when editing tab separated files.

This mapping, when applied over lines with tab separated values, will transpose the matrix made of
lines and tabs. Check out the GIF below to get a better understanding of how this works.

```vim
" Transpose tab separated values in selection or over motion.
nnoremap <silent> gt :set opfunc=Transpose<CR>g@
vnoremap <silent> gt :<C-u>call Transpose(1)<CR>
fun! Transpose(...) abort
    let vis = get(a:000, 0, 0)
    let marks = vis ? '<>' : '[]'
    let [_, l1, c1, _] = getpos("'" . marks[0])
    let [_, l2, c2, _] = getpos("'" . marks[1])
    let l:lines = map(getline(l1, l2), 'split(v:val, "\t")')
    py3 <<EOPYTHON
import vim
from itertools import zip_longest
out = list(zip_longest(*vim.eval('l:lines'), fillvalue=''))
EOPYTHON
    let out = map(py3eval('out'), 'join(v:val, "\t")')
    call append(l2, out)
    exe l1 . ',' . l2 . 'delete _'
endfun
```

The keys I'm hitting in the GIF is <kbd>gtip</kbd>. I'm transposing the lines in the inner
paragraph.

Note that I'm using `:py3` for this, so, `+python3` would be necessary for this to work. I might
port it to Vimscript one of these days, hopefully.

## Strip Trailing Spaces

I know trailing whitespace doesn't bother a lot of people much, but it does upset me. Most of the
solutions I found online to remove trailing whitespace operate on the whole file. I wanted it to
work with the lines over a motion, like inner paragraph etc. Of course, I could just visually select
the text object and then do a `:s/\s\+$//`, but of course that's too much effort.

```vim
" Strip all trailing spaces in the selection, or over motion.
nnoremap <silent> <Leader>x :set opfunc=StripRight<CR>g@
vnoremap <silent> <Leader>x :<C-u>call StripRight(1)<CR>
fun! StripRight(...) abort
    let cp = getcurpos()
    let marks = get(a:000, 0, 0) ? '<>' : '[]'
    let [_, l1, c1, _] = getpos("'" . marks[0])
    let [_, l2, c2, _] = getpos("'" . marks[1])
    exe 'keepjumps ' . l1 . ',' . l2 . 's/\s\+$//e'
    call setpos('.', cp)
endfun
```

The above snippet defines a mapping, <kbd>,x</kbd> which operates on a motion and removes trailing
whitespace. There's some nice additions to this, in that it works in visual mode as well, and that
the cursor doesn't move as a result of this operation.

Removing trailing whitespace inside current paragraph is now <kbd>,xip</kbd>!

## Append character over motion

This mapping lets me add a character at the end of all lines over a motion. So, like,
<kbd>ga;ip</kbd> would add a semicolon to every line inside the paragraph.

I use this mostly to add commas or tab characters when working with CSV (or tab-separated files).

```vim
" Append a letter to all lines in motion.
nnoremap <silent> <expr> ga <SID>AppendToLines('n')
xnoremap <silent> ga :<C-u>call <SID>AppendToLines(visualmode())<CR>

fun s:AppendToLines(mode) abort
    let c = getchar()
    while c == "\<CursorHold>" | let c = getchar() | endwhile
    let g:_append_to_lines = nr2char(c)
    if a:mode ==? 'n'
        exe 'set opfunc=' . s:SID() . 'AppendToLinesOpFunc'
        return 'g@'
    else
        call s:AppendToLinesOpFunc('v')
    endif
endfun

fun s:AppendToLinesOpFunc(type) abort
    let marks = a:type ==? 'v' ? '<>' : '[]'
    for l in range(line("'" . marks[0]), line("'" . marks[1]))
        call setline(l, getline(l) . g:_append_to_lines)
    endfor
    unlet g:_append_to_lines
endfun
```

This may seem pointless in that, it's not very hard to do this with visual block mode. Sure. On that
note, even <kbd>A</kbd> is pretty pointless, it can be done with just <kbd>\$a</kbd>, right? No. The
point here is not about having a shorter key sequence to do this, but a more semantic one. Just like
<kbd>A</kbd> spells append at end of line, to me, <kbd>ga;ip</kbd> spells adding semicolon to every
line in the paragraph. Personally, I think better this way.

## Conclusion

Text objects in Vim (and motions, for the most part) have effectively solved the problem of being
able expressively select a piece of text to work on. However, in my opinion, the kind of work that
can be done on such text is equally (if not more) important. Try to identify what you often do after
selecting text with text objects and see if you can turn it into an operator mapping like those in
this write-up.

This one is shorter than usual and that's not because of lack of content, it's more because of
terrible planning on my part. Nevertheless, stay tuned for more in this series!


[first-article]: ../automating-the-vim-workplace/
[vartabstop]: https://vimhelp.org/options.txt.html#%27vartabstop%27
