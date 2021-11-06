---
title: The Magic of AutoHotkey
tags: autohotkey, productivity, windows, automation, workflow
reddit_url: r/AutoHotkey/comments/fbn7vv
description: >
    My automation stack for day-to-day working, that's built on Autohotkey over six years. Contains
    lots of tips and examples for automating small trivial tasks on Windows with Autohotkey.
---

For the past several years, my primary work station has been Windows 7. After the initial swearing
at how things work differently (coming from Linux), I got used to it and started to really like it,
in some ways. A big part of the reason for that on Windows is [AutoHotkey][]. I will document my
automations and experiences over the years in this two-part article series.

This article is part of a series:

1. Part 1 (this article).
1. [Part 2](../the-magic-of-autohotkey-2/)

[TOC]

[AutoHotkey][] is an open-source programming language for Windows, that lends itself extremely well
to tasks within the GUI scripting and automation domains. The hotkey functionality is particularly
good, something I haven't found in any other general purpose programming language ([AutoIt][] most
likely comes close, but I've never tried it so can't speak for it).

The language itself may seem a bit flaky around the syntax and some of the constructs, but once we
get used to them, we can leverage the powerful engine underneath it. That, combined with the
well-written documentation, makes AutoHotkey a must-have tool for any Windows power user.

Some of the hotkeys I use (few that I can't show off here) are so well integrated into my daily
workflow, that my fingers just flow on the keyboard and things happen on screen that are hard to
follow for others.

> Any sufficiently advanced technology is indistinguishable from magic.
>
> -- *Clarke's Third Law, 1973*

In these articles, I'll share some of the hotkeys I use, how I came about them and how they improve
my workflow. It is not a beginner's AutoHotkey tutorial, that would be the official documentation or
the many other resources available online.

A lot of the stuff in this article is made possible by a lot of help from all over the internet, and
especially the AutoHotkey forums. Due to most of it being at least a few years old, I don't have the
exact source links. So, thank you everyone!
{: .note }

## The Setup

I usually have one AutoHotkey script running at all times (called `master.ahk`). I `#Include` other
scripts into this so that all my hotkeys and automations aren't just dumped into one large
`master.ahk`. It starts off with the following:

```ahk
#NoEnv
#SingleInstance force
#Warn

SendMode Input
SetWorkingDir %A_ScriptDir% ; Default in autohotkey v2.
AutoTrim, Off ; Default in autohotkey v2.
SetTitleMatchMode RegEx
SetNumlockState, AlwaysOn

EnvGet, homedir, USERPROFILE
```

Most of this I learned to be a best practice from the documentation and from the forums. Please look
up the documentation for these individual directives, I won't repeat them here.

## The Common Magic

These are essentials that are general enough that I believe everyone using AutoHotkey should have.
Let's quickly run these down so we can move on to more exciting stuff.

### Reload AutoHotkey Script

The script `master.ahk` that is running in the background at all times contains some of my hotkeys
and the rest are `#Include`-ed from other AutoHotkey scripts. I include the below snippet in this
script and when I hit <kbd>#+r</kbd>, the changes in `master.ahk` and any included scripts are
reloaded.

```ahk
#+r::Reload
```

All script snippets discussed here, if and when added to your master script, would start working
fine with a reload like above. No need to quit it and start again.
{: .note }

### Open the Toolbar Calendar

It's really sad that there's no default hotkey to have a calendar pop open on Windows. Clicking on
the time displayed at the right of the toolbar does show a handy calendar, but there's no hotkey for
it. The following solves this exact problem. We use the <kbd>#b</kbd> hotkey which gives focus to
the system tray. Then we navigate to the time and hit the <kbd>{Enter}</kbd> key.

```ahk
#i::Send #b{Left}{Enter}
```

There's a problem with this though. Once the calendar opens up, and we close it by hitting the
<kbd>Escape</kbd> key, the focus is not returned to the window that had focus originally. The
workaround for me has been to do <kbd>Alt+Tab</kbd> a couple of times and we're back to work.

It's still arguable how useful this solution is. The pop-up Calendar has very limited functionality.
The most annoying this is probably that I spend a few seconds selecting the month I want to look at
and accidentally click on another window and that Calendar is gone! After a lot of swearing, I
attempted to solve this problem and built [calendar.sharats.me](https://calendar.sharats.me). It's
super-quick, no-login-required, light-weight, just a calendar to look at, and mark dates to top. Do
check it out! Thanks.
{: .note }

### Hide the Show Desktop Button

Every time my mouse moves to the bottom right corner, all my windows go transparent, and *almost*
reduce me to swearing again. Now, I know we can turn this behaviour off by disabling Aero or some
other setting and I can even agree that this feature can be useful. But to me, firstly, I hardly
keep anything on my Desktop so even it's existence is quite useless to me. Secondly, even if I
wanted to look at the desktop, it's a quick <kbd>#d</kbd> away, which is much faster considering my
fingers are almost always on the keyboard.

So I decided to hide the "Show Desktop" button with the following snippet:

```ahk
Control, Hide, , TrayShowDesktopButtonWClass1
    , ahk_class Shell_TrayWnd ahk_exe explorer.exe
```

This doesn't reclaim the space occupied by the button, but the button disappears and the above
problem goes away, so, I'm not complaining.

### Type Clipboard Contents

Remember how some websites (especially bank websites) disallow pasting values into inputs. This is
extremely annoying when using a password manager or when I want to just paste something. I've tried
several different solutions to this, and the current answer I have with AutoHotkey has served me the
best.

```ahk
#v::SendInput, {Raw}%Clipboard%
```

The idea is that instead of sending a paste operation, we have AutoHotkey *type out the contents of
the clipboard*. This has the additional benefit of stripping any formatting in the text in the
clipboard, if for instance, we've copied something from a website or a word document with heavy
formatting.

## Close on Escape Key

There are some windows that I'd love to close with just a tap on the <kbd>Escape</kbd> key, but they
don't. A few examples of where I (instinctively) expect this are the photo viewer, font viewer, the
playlist in VLC etc. Then there's another set of windows that I found myself trying to close by
hitting <kbd>^w</kbd> (this intuition likely comes from it's behaviour in Firefox and Chrome).
Either way, I needed these keys to act the way I was expecting them to.

There's two parts to the solution to this. First, we define the hotkeys to close the windows on
**window groups**:

```ahk
#IfWinActive ahk_group CloseOnEsc
Escape::PostMessage 0x112, 0xF060
#IfWinActive ahk_group CloseOnCW
^w::PostMessage 0x112, 0xF060
#IfWinActive
```

What we're doing here is define two hotkeys. First, for all windows in the group called
`CloseOnEsc`, define the hotkey <kbd>Escape</kbd> to close the window (the `PostMessage` part, which
we'll get to in a bit). Second, a similar hotkey on <kbd>^w</kbd> for windows in the group
`CloseOnCW`.

Now, you might've noticed that we don't use the `WinClose` command to close the window. The reason
is that for some applications (such as Lync), the `WinClose` command *quits* the application instead
of just sending it back to the tray. The `PostMessage` command above would behave exactly like
hitting the red close button at the top right of the window.

In the second part of this exercise, we add windows to the groups:

```ahk {"linenos": true}
; Windows that should just disappear on ESC, but don't already.
GroupAdd, CloseOnEsc, ahk_class Photo_Lightweight_Viewer
GroupAdd, CloseOnEsc, ahk_class ConsoleWindowClass
GroupAdd, CloseOnEsc, Skype for Business
GroupAdd, CloseOnEsc, Vivaldi Settings ahk_exe vivaldi.exe
GroupAdd, CloseOnEsc, ahk_class FontViewWClass ahk_exe fontview.exe
GroupAdd, CloseOnEsc, Playlist ahk_exe vlc.exe

; Windows that should close with C-w.
GroupAdd, CloseOnCW, ahk_class Notepad ahk_exe notepad.exe
GroupAdd, CloseOnCW, ahk_class FM ahk_exe 7zFM.exe
```

This should be fairly self explanatory. We add certain windows (as identified by `WinTitle` style
filters) and add them to the two groups, using the `GroupAdd` command.

There's one special case here. The stock Windows Calculator app. This one clears the display on
hitting <kbd>Escape</kbd> key. But I wanted it to close on <kbd>Escape</kbd> **if** the display is
already cleared.

So, instead of including Calculator in the above group(s), I use the following snippet to handle
this special case.

```ahk
#IfWinActive ahk_class CalcFrame
$Escape::
CloseOrClearCalculator() {
    ControlGetText, display, Static4
    if (display == "0")
        WinClose
    else
        SendInput, {Escape}
}
#IfWinActive
```

This will close the Calculator if the display is already `"0"`, but passes the <kbd>Escape</kbd> key
otherwise.

## The Caps Lock Story

I use [SharpKeys][] to turn my <kbd>Caps Lock</kbd> key into an additional <kbd>Ctrl</kbd> Key. This
works wonders considering that the <kbd>Ctrl</kbd> key is used a lot more often than the <kbd>Caps
Lock</kbd>, but the <kbd>Caps Lock</kbd> key is a lot easier to hit than any of the <kbd>Ctrl</kbd>
keys.

If you're wondering why I don't do this with AutoHotkey, the reason is that if I did it with
AutoHotkey, it would be active *only when the script is running*. Which means the remapping isn't
active in the lock screen (where I hit <kbd>Ctrl+A</kbd> often). But since SharpKeys modifies the
registry to achieve what it does, the remapping works even in the lock screen.

Yet, sometimes I miss the original functionality of the <kbd>Caps Lock</kbd> key. So I created the
following hotkey for <kbd>#q</kbd> which will turn on Caps Lock mode, and show an annoying
always-on-top splash window alerting me to that fact. To turn it back off, it's <kbd>#q</kbd> again.

```ahk
#q::
ToggleCapsLock() {
    if GetKeyState("Capslock", "T") {
        SetCapsLockState, Off
        SplashTextOff
    } else {
        SetCapsLockState, On
        SplashTextOn, 300, , << CAPS LOCK ON >> (Win+q to turn off)
        WinSet, Transparent, 200, << CAPS LOCK ON >>
    }
}
```

This actually works surprisingly well. I use it more often than I like to admit. It feels better
than using the original <kbd>Caps Lock</kbd> key, because I get an (hard-to-ignore) overlay that
alerts me that Caps Lock is turned on.

## Inserting Snippets

Inserting snippets is an idea where a long and often used string is inserted by a rather short
sequence of keys. In AutoHotkey, this is *usually* done using [hotstrings][]. Hotstrings work *okay*
for this actually, but they don't work on every application. For me particularly, I needed them to
be working with GVim (which is where I write most of my prose), which they weren't. So, with a lot
of help from the Internet, I came up with a solution.

Instead of hotstrings, I'll use a hotkey that summons a OSD (on-screen-display) with a list of keys
and their expansions. When this window is focused, I can hit one of those keys and the windows is
immediately closed and the corresponding expansion is typed out. This has been working unchanged for
over four years for me and has never failed me.

```ahk {"linenos": true, "filename": "snippets.ahk"}
SnippetsInit() {
    Gui, Snips: Default
    Gui, Font, s18 q5, Consolas
    Gui, Color, FF0000
    Gui, Margin, 6, 6
    Gui, +AlwaysOnTop +Owner +ToolWindow -Caption +HwndSnippetsHwnd
    Gui, Add, ListView, r8 w900, Hotkey|Text

    IniRead, configText, snippets.ini, master
    Loop, Parse, configText, `n, `r
    {
        parts := StrSplit(A_LoopField, "=", " `t")
        LV_Add("", parts[1], parts[2])
    }
}

SnippetsShow() {
    global SnippetsMap
    Gui, Snips: Show, NoActivate
    Input, key, L1 T3
    Gui, Snips: Hide
    if (ErrorLevel != "Timeout") {
        IniRead, value, snippets.ini, master, %key%, __SNIPPETS_KEY_NOT_FOUND__
        if (value != "__SNIPPETS_KEY_NOT_FOUND__")
            SendInput, %value%
        else
            MsgBox, No snippet found for %key%.
    }
}
```

I have the above in a module called `snippets.ahk`, which I include in my master script. To use,
first, I need a `snippets.ini` file in the same directory with expansions. I have things like the
following:

```ini
[master]
u = sharat87
m = yeahhereismyaddress@gmail.com
i = {+}91 AND MY PHONE NUMBER
s = https://sharats.me/
```

There's more snippets on my system, this is just a preview, of course, duh!

The next step is to include this module in our master script:

```ahk
#Include snippets.ahk
SnippetsInit()
```

Finally, we define a hotkey to summon the snippets window. I use <kbd>^;</kbd>.

```ahk
^;::SnippetsShow()
```

That's it! Here it is in action:

![Snippets tool demo]({static}/static/autohotkey-snippets.gif)

## Window Watcher

My window watcher module (written as a `window-watcher.ahk`) lets me define actions to be taken when
new windows with certain properties show up.

For example, I want all command line windows to always be moved to the top right corner or the
screen. As another example, there's some windows that open up with a window size equal to the whole
screen, but are not maximized. This one is particularly annoying since I have a habit of throwing my
mouse to the top right corner and clicking to close the window. But since this window is not
maximized, I end up accidentally closing the window behind. So, I want such windows to be maximized
as soon as they open.

To address this, I have a `window-watcher.ahk` module that defines the logic of constantly polling
the visible windows and detecting if anything is opened or closed. This module defines the function
`WindowWatcherInit` (among others), which needs to be called once to initialize the polling timer.

```ahk {"linenos": true, "filename": "window-watchers.ahk"}
WindowWatcherInit() {
    static initDone := false

    if (initDone)
        return
    initDone := true

    SetTimer, WindowWatcherPollForNewWindows
}

WindowWatcherTrigger(wParam, hwnd) {
    if (wParam == "Created") {
        OnWindowCreated(hwnd)
    ; } else if (wParam == "Destroyed") {
    }
}

WindowWatcherPollForNewWindows() {
    static windows := ""
    WinGet, wins, List, , , ,
    newWindows := Object()

    Loop, %wins%
    {
        this_id := wins%A_Index%
        newWindows[this_id] := 1
        if (windows && !windows[this_id])
            WindowWatcherTrigger("Created", this_id)
    }

    for wid, p in windows {
        if (!newWindows[wid])
            WindowWatcherTrigger("Destroyed", wid)
    }

    windows := newWindows
}
```

From then on, any time a new window is detected, the `OnWindowCreated` function is called with the
new window's `hwnd` passed as the only argument. In this function, I match this window ID with
various types of windows and take the action I need. Here's a short preview of that function (in
reality, the function is 81 lines long in my master script).

```ahk {"linenos": true}
OnWindowCreated(hwnd) {
    global homedir

    ; Close "Illegal IP Address" alerts.
    } else if (WinExist("Application Error ahk_exe jweblauncher.exe ahk_id " . hwnd)) {
        PostMessage, 0x112, 0xF060, , ahk_id %hwnd%

    ; Close "Kyeboard History Utility" alerts.
    } else if (WinExist("Keyboard History Utility ahk_exe WerFault.exe ahk_id " . hwnd)) {
        ControlClick, Close the program, ahk_id %hwnd%

    ; When a command window opens, move it to top-right.
    } else if (WinExist("ahk_class ConsoleWindowClass ahk_id " . hwnd)) {
        WinGetPos, , , w, , ahk_id %hwnd%
        x := A_ScreenWidth - w
        WinMove, ahk_id %hwnd%, , %x%, 0

    ; Maximize windows that open unmaximized but occupy almost-entire screen.
    } else if (WinExist("ahk_id " . hwnd . " ahk_group MaximizeOnOpen")) {
        WinMaximize, ahk_id %hwnd%

    } else {
        WinGetPos, , , width, height, ahk_id %hwnd%
        if (width >= A_ScreenWidth && height > .9 * A_ScreenHeight)
            WinMaximize, ahk_id %hwnd%

    }

}
```

There are other methods to achieve the window-watching without polling and I encourage you to try
them out if you're not comfortable with polling, like with using `RegisterShellHookWindow`. In my
experience, such solutions seemed to miss some windows and were able to catch only a small limited
set of the windows there were opening. So I went with polling, which was less efficient, but has
been more reliable for me.

## Mess with Images in Clipboard

This is a little trick that's powered by [ImageMagick][]. I add a menu item in the tray icon's
context menu called `"Add border to image in clipboard"`, which is quite self-explanatory!

```ahk
Menu, Tray, Add, Add border to image in clipboard, AddBorderToImageInCb
```

The callback for this menu item invokes the following function. Here, we just run the appropriate
ImageMagick command and show a little dialog when it's done so we can go ahead and paste the
bordered image.

```ahk
AddBorderToImageInCb() {
    RunWait, C:\tools\ImageMagick\magick.exe convert clipboard:myimage -bordercolor "#0099FF" -border 6x6 clipboard:, , Hide
    MsgBox, Added border to image in clipboard.
}
```

I use this a lot with screenshot snips (taken with the snipping tool or copied from paint), before
pasting into an email. Having a border around images in emails makes them stand out and have a
distinct visual.

## Periodic Time Display

As an alternative to the popular [Pomodoro Technique][], I have a small non-intrusive OSD show up
with the current time at the bottom of my screen every 20 minutes. That is, I get a small blue OSD
at `:00` times, a small green OSD at `:20` times and a small orange OSD at `:40` times. Here's
preview of how this looks:

![Time OSD example view]({static}/static/autohotkey-time-osd.png)

Again, for this, I have a separate module called `time-osd.ahk` which I `#Include` in the master
script and call it's init function. (This init-function-in-a-separate-module is something I came up
with that was working well enough, I have no idea if it's a best practice).

```ahk {"linenos": true, "filename": "time-osd.ahk"}
TimeOSDInit() {
    global TimeOSDLabel
    SetTimer, TimeOSDPulse, 1000
    Gui, TimeOSD:Default
    Gui, +LastFound +AlwaysOnTop +ToolWindow -Caption
    Gui, Font, s18, Calibri
    Gui, Margin, 0, 0
    Gui, Add, Text, cWhite vTimeOSDLabel gTimeOSDClose w250 h36 Center
}

TimeOSDPulse() {
    static lastTime := ""

    if (IsFunc("IsWindowFullScreen") && IsWindowFullScreen("A"))
        Return

    FormatTime, currTime, , h:mm tt

    if (lastTime == currTime || A_TimeIdlePhysical > 600000)
        Return

    if (RegExMatch(currTime, ":00"))
        TimeOSDShow(currTime, "268BD2")
    else if (RegExMatch(currTime, ":20"))
        TimeOSDShow(currTime, "859900")
    else if (RegExMatch(currTime, ":40"))
        TimeOSDShow(currTime, "CB4B16")

    lastTime := currTime
}

TimeOSDShow(timeText, bg) {
    Gui, TimeOSD:Default
    Gui, Color, %bg%
    GuiControl, Text, TimeOSDLabel, It's %timeText% already!
    y := A_ScreenHeight - 120
    Gui, Show, xCenter y%y% NoActivate
    SetTimer, TimeOSDClose, -10000
}

TimeOSDClose() {
    Gui, TimeOSD:Cancel
}
```

With this, clicking on the OSDs will close them, or, they'll disappear in 10 seconds.

To use this, I just include the following in my master script.

```ahk
#Include time-osd.ahk
TimeOSDInit()
```

## Vim Keys for Sumatra PDF

This one probably only makes sense if your fingers are used to hitting [Vim][]'s hotkeys. I wanted
some of Vim's simple hotkeys for navigating the document on Sumatra PDF (my PDF reader of choice on
Windows). The following snippet that I currently use, gets me <kbd>d</kbd> (like Vim's
<kbd>&lt;C-d&gt;</kbd>), <kbd>e</kbd> (like Vim's <kbd>&lt;C-u&gt;</kbd>), <kbd>n</kbd>,
<kbd>+n</kbd> (like Vim's <kbd>N</kbd>), <kbd>x</kbd> (to close a tab), <kbd>g</kbd> and
<kbd>+g</kbd> (like Vim's <kbd>g</kbd> & <kbd>G</kbd>).

```ahk {"linenos": true}
#IfWinActive ahk_exe SumatraPDF.exe ahk_class SUMATRA_PDF_FRAME
$d::
$e::
    SumatraKeys := {d: "j", e: "k"}
    ControlGetFocus, ctrl
    if (ctrl == "Edit1" or ctrl == "Edit2") {
        Send %A_ThisHotkey%
    } else {
        k := SumatraKeys[StrReplace(A_ThisHotkey, "$", "")]
        {% raw %}Send {%k% 22}{% endraw %}
    }
    Return

$n::
    ControlGetFocus, ctrl
    if (ctrl == "Edit1" or ctrl == "Edit2")
        Send, n
    else
        Send, {F3}
    Return

$+n::
    ControlGetFocus, ctrl
    if (ctrl == "Edit1" or ctrl == "Edit2")
        Send, N
    else
        Send, +{F3}
    Return

$x::
    ControlGetFocus, ctrl
    if (ctrl == "Edit1" or ctrl == "Edit2")
        Send, x
    else
        Send, ^w
    Return

+g::Send, {End 2}

#IfWinActive Go to page ahk_exe SumatraPDF.exe ahk_class #32770
g::Send, {Escape}{Home}

#IfWinActive
```

This looks like a sad, long, hairy piece of code (probably because it is), but it works so I let it
be. This sentiment shows up a lot when dealing with AutoHotkey code. But it works, and it works
really well.

## Conclusion

AutoHotkey's language may have it's quirks, but it's a very powerful tool when it comes to hotkeys.
I have come to the point that working on Windows is practically hair-wrecking for me without
AutoHotkey (and my scripts, of course). I encourage you to check it out and explore the
possibilities.

I intend to publish a sequel to this article in a week or two, so, stay tuned or subscribe!


[AutoHotkey]: https://www.autohotkey.com/
[AutoIt]: https://www.autoitscript.com/site/
[Pomodoro Technique]: https://en.wikipedia.org/wiki/Pomodoro_Technique
[SharpKeys]: https://github.com/randyrants/sharpkeys
[Vim]: https://www.vim.org/
[ImageMagick]: https://imagemagick.org/index.php
[hotstrings]: https://www.autohotkey.com/docs/Hotstrings.htm
[ealt-1]: https://www.xyplorer.com/
[ealt-2]: https://www.zabkat.com/
[ealt-3]: https://www.gpsoft.com.au/
[ealt-4]: https://freecommander.com/en/summary/
[explorer-lib]: https://autohotkey.com/board/topic/60985-get-paths-of-selected-items-in-an-explorer-window/
