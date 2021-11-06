---
title: The Magic of AutoHotkey &mdash; Part 2
tags: autohotkey, productivity, windows, automation
description: >
    My automation stack for day-to-day working, that's built on Autohotkey over six years. This is
    part 2 of the "Magic of AutoHotkey" series. In this part, we look at automating the file
    explorer and using OLE objects for office applications.
---

In the previous part of [The Magic of AutoHotkey][prev-article], we looked at automating small
pieces of routine tasks with various applications, as well as identifying things that could be done
better with a quick hotkey. This is the next chapter of the story. In this article, I'll show you
how I tamed the stock file explorer as well as connecting to office applications with OLE to provide
additional rich functionality.

This article is part of a series:

1. [Part 1](../the-magic-of-autohotkey/)
1. Part 2 (this article).

[TOC]

## File Explorer Magic

The file explorer is probably my most used application during work. Yet, it doesn't feel like it's
tuned for a power user. May be that's also why [there's][ealt-1] [so][ealt-2] [many][ealt-3]
[alternatives][ealt-4] to file explorers. I've tried a few of them in the past, but the best has
been to add exactly the few things I needed in the native file explorer, using AutoHotkey. I'll run
through those here.

As is the case in the previous part, I have a module called `file-explorer-tweaks.ahk` which is
`#Include`-ed in my master script.

To start, we define a window group, which includes all file explorer windows. We later use this
group to define hotkeys that we want to work *only* on the file explorer windows.

```ahk
GroupAdd, FileListers, ahk_class CabinetWClass
GroupAdd, FileListers, ahk_class WorkerW
GroupAdd, FileListers, ahk_class #32770, ShellView
```

This group now matches the file explorer windows, desktop and the file open dialog windows.

### Focus Location Editor

Almost all the web browsers today have the default hotkey <kbd>^l</kbd> which focuses the location
bar, and selects everything in it. But in the file explorer, this is <kbd>!d</kbd>. Habits rule and
I constantly hit <kbd>^l</kbd> in the file explorer window when I wanted to change something in the
location bar. Obviously, it didn't work and it would drive me crazy. Until I added the following to
save me from insanity:

```ahk
#IfWinActive ahk_group FileListers
^l::SendInput !d
```

While this works fine on the face of it, if I hit <kbd>Escape</kbd> after focusing the location bar
like this, the focus is not returned to the file list. I haven't figured out a solution to that yet,
so that one's open.

### Open Command Window

The file explorer has a nice less-known trick. If I right click without any files selected and with
the <kbd>Shift</kbd> key held down, I get an extra option in the context menu, called "Open command
window here". Clicking on that menu item will open a new command prompt window in the current
directory. This is extremely convenient if you need the command window often (which you might,
especially if you're a software developer).

But this needed the mouse. I wanted to do this with the keyboard. Turns out it's easier than one
might think:

```ahk
#IfWinActive ahk_group FileListers
^!t::SendInput !dcmd{Enter}
```

Here, we define the <kbd>^!t</kbd> hotkey which will focus the location bar and type in `cmd` and
hit the <kbd>Enter</kbd> key. This will actually open up a command window *in the current
directory*.

### Folder Shortcuts

Folder shortcuts is where I define a hotkey that will navigate to a specific directory, always. For
example, while in a file explorer, hitting <kbd>^h</kbd> should navigate to the home folder, hitting
<kbd>^j</kbd> should navigate to the Downloads folder (this key opens the downloads view in web
browsers, see what I did there?).

```ahk
#IfWinActive ahk_group FileListers
^h::Send !d%homedir%{Enter}
^j::Send !d%homedir%\Downloads{Enter}
^y::Send !dLibraries\Documents{enter}
^k::Send !dC:\work{Enter}
^t::Send !dC:\tools{Enter}
^b::Send !dC:\labs{Enter}
```

This snippet uses the `homedir` variable defined in the [previous article][homedir-section].

On the face of it, these are very simple hotkeys. We pass <kbd>!d</kbd> to focus the location input
and type in the location where we want to go to. Simple & effective. They serve sort of like quick
access bookmarks and are probably my most used hotkeys defined with AutoHotkey overall, by a margin.

### Better Hotkeys for Directional Navigation

In the previous section, we dealt with navigating to absolution locations. But how about directional
navigation, where we want to go back or forward or even up the directory chain?

The default hotkeys for this leverage the arrow keys, which require taking my hands off the
keyboard's home row. So, I'm using the following keys for these three operations, which are inspired
by similar behavior in Vim (again!).

```ahk
; Navigate with the keyboard better!
#IfWinActive ahk_group FileListers
^o::SendInput, !{Left}
^i::SendInput, !{Right}
^u::SendInput, !{Up}
```

To top it, I have also defined mouse "hotkeys" for these three actions. I rarely use these nowadays,
but they're still there for when I already have a hand on the mouse.

```ahk
; Navigate with the mouse!
#IfWinActive ahk_group FileListers
!WheelUp::SendInput, !{Up}
^WheelUp::SendInput, !{Left}
^WheelDown::SendInput, !{Right}
```

Pretty self-explanatory really.

### Select Files by Pattern

I particularly love this one. When I trigger this hotkey, a little prompt shows up where I enter a
regular expression and then every file in the current folder that matches this pattern will be
selected. The first time I used this on a folder with ~300 files, I practically had tears in my eyes
at how easy it was to make the file selection by a pattern.

So, here's the code for this:

```ahk {"linenos": true}
; Get selected files in explorer and more:
; http://www.autohotkey.com/board/topic/60985-get-paths-of-selected-items-in-an-explorer-window/
#IfWinActive ahk_group FileListers
^s::
SelectByRegEx() {
    static selectionPattern := ""
    WinGetPos, wx, wy
    ControlGetPos, cx, cy, cw, , DirectUIHWND3
    x := wx + cx + cw/2 - 200
    y := wy + cy
    InputBox, selectionPattern, Select by regex
        , Enter regex pattern to select files that CONTAIN it (Empty to select all)
        , , 400, 150, %x%, %y%, , , %selectionPattern%
    if ErrorLevel
        Return
    for window in ComObjCreate("Shell.Application").Windows
        if WinActive("ahk_id " . window.hwnd) {
            pattern := "S)" . selectionPattern
            items := window.document.Folder.Items
            total := items.Count()
            i := 0
            showProgress := total > 160
            if (showProgress)
                Progress, b w200, , Matching...
            for item in items {
                match := RegExMatch(item.Name, pattern) ? 17 : 0
                window.document.SelectItem(item, match)
                if (showProgress) {
                    i := i + 100
                    Progress, % i / total
                }
            }
            Break
        }
    Progress, Off
}
```

The code is not very pretty, but oh well. It works well and I'd rather not touch it.

Here's a little **mute** video recording of this at work:

Video: autohotkey-select-by-pattern.mp4

### Batch Rename

This is actually built to be invoked as a separate AutoHotkey process, not to be `#Include`-ed into
a master script. That's because the GUI is slightly more complex than what we've seen in previous
sections and I didn't bother to make it work well as a module.

```ahk {"linenos": true, "filename": "batch-rename.ahk"}
#NoEnv
#NoTrayIcon

active_hwnd := WinActive("ahk_class CabinetWClass")
If (active_hwnd) {
    for window in ComObjCreate("Shell.Application").Windows
        If (active_hwnd == window.hwnd) {
            parent := uriDecode(StrReplace(window.LocationURL, "file:///", "", , 1))
            ShowGui()
        }
}

ShowGui() {
    global active_hwnd, parent, SourcePattern, TargetPattern, WindowListView
    Gui, Font, s10 q5, Segoe UI
    Gui, Margin, 6, 6
    Gui, +Owner%active_hwnd%
    Gui, Add, Text, , Search pattern:
    Gui, Add, Edit, r1 w300 vSourcePattern gInputChanged -WantReturn X+6 Section
    Gui, Add, Text, X+6, Full regex is supported
    Gui, Add, Text, XM, Replacement:
    Gui, Add, Edit, r1 w300 vTargetPattern gInputChanged -WantReturn XS YP
    Gui, Add, Text, X+6, Use $1, $2, ${10}, ${named}, $U1, $U{10}, $L2, $T0 etc.
    Gui, Add, Button, Default gDoRename XM w80, Apply
    Gui, Add, Button, gShowHelp X+6 w80, Help
    Gui, Add, ListView, Grid r12 w800 vWindowListView XM, Replacements|Current name|Renamed to

    imList := IL_Create(2)
    LV_SetImageList(imList)
    IL_Add(imList, "check.png", 0xFFFFFF, 1)
    IL_Add(imList, "error.png", 0xFFFFFF, 1)
    ; IL_Add(imList, "shell32.dll", 145)
    ; IL_Add(imList, "shell32.dll", 234)

    Gui, Show, , Rename with Regex: %parent%
}

InputChanged() {
    global parent, SourcePattern, TargetPattern
    GuiControlGet, SourcePattern
    GuiControlGet, TargetPattern
    LV_Delete()
    Loop, Files, %parent%\*, FD
    {
        toName := RegExReplace(A_LoopFileName, SourcePattern, TargetPattern, count)
        icon := 1
        If (A_LoopFileName == toName)
            icon := 3
        Else if (FileExist(parent . "/" . toName))
            icon := 2
        LV_Add("Icon" . icon, count, A_LoopFileName, toName)
    }
    LV_ModifyCol()
}

DoRename() {
    global parent, SourcePattern, TargetPattern
    Gui, Submit

    If (SourcePattern != "")
        Loop %parent%\* {
            toName := RegExReplace(A_LoopFileName, SourcePattern, TargetPattern)
            FileMove, %parent%\%A_LoopFileName%, %parent%\%toName%
        }

    GuiClose()
}

GuiEscape() {
    GuiClose()
}

GuiClose() {
    ExitApp
}

uriDecode(str) {
    Loop
        If RegExMatch(str, "i)(?<=%)[\da-f]{1,2}", hex)
            StringReplace, str, str, `%%hex%, % Chr("0x" . hex), All
        Else Break
    Return, str
}

ShowHelp() {
    help=
    (
## Pattern:

The pattern to search for, which is a Perl-compatible regular expression (PCRE). The pattern's options (if any) must be included at the beginning of the string followed by a close-parenthesis. For example, the pattern "i)abc.*123" would turn on the case-insensitive option and search for "abc", followed by zero or more occurrences of any character, followed by "123". If there are no options, the ")" is optional; for example, ")abc" is equivalent to "abc".

## Replacement:

The string to be substituted for each match, which is plain text (not a regular expression). It may include backreferences like $1, which brings in the substring from Haystack that matched the first subpattern. The simplest backreferences are $0 through $9, where $0 is the substring that matched the entire pattern, $1 is the substring that matched the first subpattern, $2 is the second, and so on. For backreferences above 9 (and optionally those below 9), enclose the number in braces; e.g. ${10}, ${11}, and so on. For named subpatterns, enclose the name in braces; e.g. ${SubpatternName}. To specify a literal $, use $$ (this is the only character that needs such special treatment; backslashes are never needed to escape anything).

To convert the case of a subpattern, follow the $ with one of the following characters: U or u (uppercase), L or l (lowercase), T or t (title case, in which the first letter of each word is capitalized but all others are made lowercase). For example, both $U1 and $U{1} transcribe an uppercase version of the first subpattern.

Nonexistent backreferences and those that did not match anything in Haystack -- such as one of the subpatterns in "(abc)|(xyz)" -- are transcribed as empty strings.
)
MsgBox, %help%
}
```

Put this script at a convenient location, probably right next to your master script, and add the
following hotkey to your master script:

```ahk
#IfWinActive ahk_group FileListers
^+b::Run batch-rename.ahk
```

Here's a little **mute** video recording of some usage examples of this tool:

Video: autohotkey-rename-by-regex.mp4

If you're using this, please keep caution. Please inspect the previous table before clicking on the
"Apply" button. If it ends up messing your files up, don't hold me responsible. I'm sharing this
without warranty. As any source code block on this website, this is shared here with [ISC
License](/licenses/isc/).
{: .note }

### Copy Paths of Selected Files

This, again, is actually *partly* fulfilled by default Windows functionality. When we
<kbd>Shift+Right Click</kbd> on a file, we get the option to "Copy as path", which works fine for
simple cases. But I wanted the following additional things for this feature:

1. A keyboard hotkey, like <kbd>^+c</kbd>.
1. No surrounding double quotes.
1. Work with multiple files being selected. Copy each file's path as one line.

For this, I defined the following <kbd>^+c</kbd> hotkey on the file explorer windows. 

```ahk
#IfWinActive ahk_group FileListers
^+c::
    Clipboard := JoinArrayContents(Explorer_GetSelected())
    Return
```

This will get a list of all selected files in the current explorer window and join them into a
single string. The `Explorer_GetSelected` function comes from [this AutoHotkey forum
post][explorer-lib] and the `JoinArrayContents` is given below:

```ahk
JoinArrayContents(arr, delimiter="`n") {
    content := ""
    for index, item in arr {
        if index > 1
            content := content . delimiter
        content := content . item
    }
    return content
}
```

Now I can select one or more files, hit <kbd>^+c</kbd> and the full paths of *all* the selected
files will end up in my clipboard.

### Copy Contents of Selected Files

This one, although sounds similar to the previous section, is quite different and useful in a very
different way. Where the previous section's hotkey copies the selected files' *paths*, this hotkey
is intended to copy the selected files' *contents* as a whole.

I have a few (several?) small text files with snippets, template messages, etc. With this, I just
select one or multiple files and hit <kbd>Ctrl+Shift+x</kbd> and I'm ready to paste their contents.

```ahk
#IfWinActive ahk_group FileListers
^+x::
    CopySelectedFileContents() {
        files := Explorer_GetSelected()
        content := ""
        for i, file in files {
            FileRead, text, %file%
            if i > 1
                content := content . "`n`n"
            content := content . text
        }
        Clipboard := content
    }
```

This is the same `Explorer_GetSelected` I referred to in the previous section. However, in the above
hotkey definition, instead of setting the paths to `Clipboard`, we set the contents of the files.

Just like the previous hotkey, I can select multiple *text* files and hit <kbd>^+x</kbd> and the
contents of all selected files will end up in my clipboard, separated by two blank lines.

This doesn't work with images yet though. Still have to figure that one out.

### Create File with Clipboard Contents

This is the opposite of the previous hotkey. Here, I want whatever is in the Clipboard to be saved
to a text file in the current folder.

```ahk {"linenos": true}
#IfWinActive ahk_group FileListers
^+v::
    CreateFileWithClipboardContents() {
        loc := Explorer_GetPath()
        WinGetPos, wx, wy
        ControlGetPos, cx, cy, cw, , DirectUIHWND3
        x := wx + cx + cw/2 - 200
        y := wy + cy
        InputBox, filename, Clipboard File
            , Enter file name to paste clipboard contents in:, , 400, 120, %x%, %y%, ,
            , clip.txt
        if ErrorLevel
            Return
        filepath := loc . "\" . filename
        if (FileExist(filepath)) {
            MsgBox, 1, Overwrite, Overwriting existing '%filename%'!
            IfMsgBox Cancel
                Return
            FileDelete, %filepath%
        }
        Fileappend, %Clipboard%, %filepath%
    }
```

The `Explorer_GetPath` function used in the above snippet is also from the same source I mentioned
in the previous sections. The way this works is when the hotkey is triggered, we are prompted to
enter the name of the file to which the clipboard's contents will be saved. Once we provide a file
name and submit, the file is created.

With this, I can copy some text out of a webpage or an email in Outlook and saving it to a text file
is a quick <kbd>^+v</kbd>. Once I created this hotkey, it became my primary way of creating new text
files. I no longer open Notepad, write (or paste) and then save the file to the desired directory.
Instead, I open the folder, use this hotkey to create the file, and then open the file in Notepad.
Somehow, it feels more natural.

This doesn't work with images either. Have to figure this one out too.

### Create Folder Hierarchy and Enter it

The file explorer has a default hotkey for creating new folders (<kbd>Ctrl+Shift+n</kbd>), but it
doesn't let us create a tree or folders at one go. To do that, we have to create a directory, enter
it, create again etc. This quickly gets tedious if it has to be done often.

As always I tried to address it with AutoHotkey.

```ahk
#IfWinActive ahk_group FileListers
^n::
CreateFolderHierarchy() {
    loc := Explorer_GetPath()
    WinGetPos, wx, wy
    ControlGetPos, cx, cy, cw, , DirectUIHWND3
    x := wx + cx + cw/2 - 200
    y := wy + cy
    InputBox, folder, Create Folder, Enter folder name/path create:, , 400, 120
        , %x%, %y%
    if ErrorLevel
        Return
    folder := StrReplace(folder, "/", "\")
    pos := RegExMatch(folder, "O)\{([^\{]+)\}", match)
    folders := []
    if (pos > 0) {
        parts := StrSplit(match.value(1), ",")
        prefix := SubStr(folder, 1, match.Pos(0) - 1)
        suffix := SubStr(folder, match.Pos(0) + match.Len(0))
        for i, part in parts {
            folders.Push(prefix . part . suffix)
        }
    } else {
        folders.Push(folder)
    }
    for i, folder in folders {
        FileCreateDir, %loc%\%folder%
    }
    Explorer_GetWindow().Navigate2(loc . "\" . folders[folders.Length()])
}
```

This uses the same explorer library I mentioned in the previous sections. When this hotkey is
triggered, we get a prompt where we can enter a folder tree (*i.e.,* folders separated by `/` or
`\\`) and they will all be created. As a bonus, we are also switched to that newly created folder
so we can start working with it right away.

Now I can hit <kbd>^n</kbd> and type in `src/main/java` or `2020-01/pics`, and all nesting structure
is created and navigated, which is usually followed by pasting some files.

## Email Selected File(s) with Outlook

Outlook is necessary tool for email at most corporate workplaces. So it's important to look at how
we use it, and what parts of it we can automate / improve.

It's also quite common to have to send files over email as attachments. Yet, considering how often
we tend to do that, it's still a tedious process. Go to outlook, start new mail, drag-drop the file
in this window, fill up the mail, send. It gets a bit better if you copy the file to clipboard and
then instead of starting a new mail with <kbd>Ctrl+n</kbd>, you could just hit <kbd>Ctrl+v</kbd> in
the Outlook Mails view and new mail will open up with file in clipboard as attachment. But I'd say
it's still not good enough.

The solution I currently use is the <kbd>Ctrl+m</kbd> hotkey for file explorers. The workflow is
that I select some files in my file explorer, hit <kbd>Ctrl+m</kbd> and a new mail window opens up
with the selected files as attachments, the message body containing the list of files for me to
edit and subject containing the list of files.

```ahk
#IfWinActive ahk_group FileListers
^m::OutlookNewMail(Explorer_GetSelected())
```

The `Explorer_GetSelected` function is from the same library I mentioned in an earlier section. The
following is the definition of the `OutlookNewMail` function:

```ahk
OutlookNewMail(attachments=0) {
    outlook := ComObjActive("Outlook.Application")
    mail := outlook.CreateItem(0)

    if (attachments != 0) {
        msg := ""
        sub := "Files: "
        for index, file in attachments {
            mail.Attachments.Add(file)
            SplitPath, file, basename
            msg := msg . "<p class=MsoNormal>&nbsp;&nbsp;&nbsp; "
                    . basename . "<o:p></o:p></p>"
            if (attachments.Length() == 1)
                sub := "File: " . basename
            else if (index == attachments._MaxIndex())
                sub := sub . " & " . basename
            else if (index == attachments._MinIndex())
                sub := sub . basename
            else
                sub := sub . ", " . basename
        }

        FileRead, emailTpl, email.tpl.txt
        mail.HTMLBody := StrReplace(emailTpl, "$$MESSAGE$$", msg . "</ul>")
        mail.Subject := sub
    }

    mail.Display
}
```

AutoHotkey supports connecting to OLE objects, which means we can create hotkey that create rich
interactions with Office applications like Outlook. We leverage this in the above function.

All I have to do now, is fill up the "To:" field and hit <kbd>Ctrl+Enter</kbd>. I've been loving
this ever since.

Note, of course, that since this connects to the Outlook OLE object, Outlook needs to be running for
this work.
{: .note }

### Global Hotkey for New Mail

If you've noticed, the above function's `attachments` argument has a default value. If this argument
is not provided, we just get a blank email window open up. This is convenient on its own.  So I have
it as a *global* hotkey:

```ahk
#c::OutlookNewMail()
```

This works really well since the new mail window opens up with my signature already filled up and
the focus is set to the "To:" field perfectly to quickly start working on my email.

## Conclusion

AutoHotkey is a powerful tool for automating all sorts of workflows on Windows. If you can get past
the quirks in the language itself, the underlying engine is very powerful. I know that over the few
years I've used it, I've only made use of a small portion of it's potential. In addition, the help
file that is shipped with AutoHotkey (right-click on the tray icon and click on "Help") is very
good. It's exhaustive, very detailed and contains lots of examples. I encourage going over it
occasionally to find interesting things to add to your workflow. Good luck!


[prev-article]: ../the-magic-of-autohotkey/
[homedir-section]: ../the-magic-of-autohotkey/#the-setup
[ealt-1]: https://www.xyplorer.com/
[ealt-2]: https://www.zabkat.com/
[ealt-3]: https://www.gpsoft.com.au/
[ealt-4]: https://www.ghisler.com/
[explorer-lib]: https://autohotkey.com/board/topic/60985-get-paths-of-selected-items-in-an-explorer-window/
