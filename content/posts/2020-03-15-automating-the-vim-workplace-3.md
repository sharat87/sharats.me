---
title: Automating the Vim workplace &mdash; Chapter Ⅲ
tags: vim, productivity
description: >
    More ideas and inspiration for identifying repeated actions in your Vim workflow and automate
    them, and improve your productivity! A follow up to the previous article on this topic.
---

This is the third installment of my [Automate the Vim workplace][first-article] article series. As
always, feel free to grab the ideas in this article or, better yet, take inspiration and inspect
your workflow to identify such opportunities.

[TOC]

Please note that all that I share below is what I'm using with Vim (more specifically, GVim on
Windows). I don't use Neovim (yet) and I can't speak for any of the below for Neovim.
{: .note }

## Copy file full path

I work with CSV files quite a bit. I spend a lot of time grooming them, fixing them etc. in Vim and
then once they're ready, I need to upload it to an internal tool. For that, the following command
has proven to be super useful.

```vim
" Command to copy the current file's full absolute path.
command CopyFilePath let @+ = expand(has('win32') ? '%:p:gs?/?\\?' : '%:p')
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

Nonetheless, I needed a quick way to condense several blank lines into a single blank line. The
following is the result of that:

```vim
nnoremap <silent> dc :<C-u>call <SID>CleanupBlanks()<CR>
fun s:CleanupBlanks() abort
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

Then, on a weekend when I was feeling particularly silly, I extended this to accept a number in
front of <kbd>dc</kbd> which specifies the number of newlines to end up with. So now, this mapping
can both condense, and expand vertical blank space to any size I want! Yay silly weekends!

## Duplicate Text in Motion

Copy-pasta is a legitimate writing and coding technique. But I do it so mindlessly and often, I
started to think of *duplicating* as a distinct operation, and not as a combination of *yanking* and
then *pasting*. But if that is so, *duplicating* some text should not mess with my registers. This
was messing with the nice semantic pool my thoughts were swimming in (!).

So I built a mapping that would let me duplicate the text over any motion (like text objects),
without touching the registers.  Following is how it's built:

```vim
" Duplicate text, selected or over motion.
nnoremap <silent> <Leader>uu :t.\|silent! call repeat#set('duu', v:count)<CR>
nnoremap <silent> <Leader>u :set opfunc=DuplicateText<CR>g@
vnoremap <silent> <Leader>u :<C-u>call DuplicateText('vis')<CR>
fun DuplicateText(type) abort
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

Additionally, if triggered in visual mode, the duplicated text is selected again in visual mode.
This quickly visually highlights for me the newly inserted text so I can get back on track as to
what I intended to do with the duplicated text.

Now, if you're aware of the `:t` (or `:copy`) command, then what I'm doing above may seem
pointlessly elaborate. To an extent, I agree. In fact, I'm using the `:t` command for the
<kbd>,uu</kbd> mapping which is for duplicating a single line. The difference is that where `:t`
only works line-wise, my implementation above can work character wise as well as line wise. For
example, <kbd>,uaw</kbd> (or just <kbd>,uw</kbd>) will duplicate a single word, just like
<kbd>,uap</kbd> will duplicate a paragraph.

## Transpose

This is another mapping I created to help me with CSV files. Specifically, this one works with
tab-separated files, which are even more awesome to edit in Vim, thanks to the [vartabstop][]
option. The next section describes how I use this when editing tab separated files.

This mapping, when applied over lines with tab separated values, will transpose the matrix made of
lines and tabs. Check out the GIF below to get a better understanding of how this works.

```vim
" Transpose tab separated values in selection or over motion.
nnoremap <silent> gt :set opfunc=Transpose<CR>g@
vnoremap <silent> gt :<C-u>call Transpose(1)<CR>
fun Transpose(...) abort
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

![Demo of transpose mapping](/img/vim-transpose.gif)

The keys I'm hitting in the GIF is <kbd>gtip</kbd>. I'm transposing the lines in the inner
paragraph.

Note that I'm using `:py3` for this, so, `+python3` would be required for this to work. I might port
it to Vimscript one of these days, hopefully.

## Using `vartabstop` to Line Up

The moment I learnt about the `vartabstop` option, I jumped on it right away, considering I worked
with tab separated files a lot. I created the following command that would scan the file's contents
and set the value of this option such that all the columns would line up perfectly, almost like a
spreadsheet.

The `vartabstop` option is not available in Neovim, which is one of the reasons I don't use it yet.
I just got too used to `vartabstop`.
{: .note }

```vim
command TabsLineUp call <SID>TabsLineUp()
fun s:TabsLineUp() abort
    py3 <<EOPYTHON
import vim
lengths = []
for parts in (l.split('\t') for l in vim.current.buffer if '\t' in l):
    lengths.append([len(c) for c in parts])
vim.current.buffer.options['vartabstop'] = ','.join(str(max(ls) + 3) for ls in zip(*lengths))
EOPYTHON
endfun
```

Note that I implemented this in Python 3, so you'll need `+python3` if you want to yank this one.
{: .note }

Here's a nice GIF showing this off! Note that although it looks like we're just adding a lot of
white space to align stuff, *no new space characters are inserted*. The document remains unchanged.
It's just the display size of tab characters is what we're changing with `vartabstop`.

![Tabs line up demo](/img/vim-tabs-line-up-demo.gif)

Finally tab separated files are easier to deal with than comma separated files.

Also, if you're into CSV and tab separated files, I recommend checking out the amazing [csv.vim][]
plugin. It makes similar use of the `vartabstop` option.

## Strip Trailing Spaces

I know trailing whitespace doesn't bother a lot of people much, but it does upset me. Most of the
solutions I found online to remove trailing whitespace operate on the whole file. I wanted it to
work with the lines over a motion, like inner paragraph etc. Of course, I could just visually select
the text object and then do a `:s/\s\+$//`, but that's too much effort!

```vim
" Strip all trailing spaces in the selection, or over motion.
nnoremap <silent> <Leader>x :set opfunc=StripRight<CR>g@
vnoremap <silent> <Leader>x :<C-u>call StripRight(1)<CR>
fun StripRight(...) abort
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
<kbd>A</kbd> spells "append at end of line", to me, <kbd>ga;ip</kbd> spells "adding semicolon to
every line in the paragraph". Personally, I think better this way.

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
[csv.vim]: https://github.com/chrisbra/csv.vim
