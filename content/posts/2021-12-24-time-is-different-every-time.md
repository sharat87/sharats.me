---
title: Time is different every time
tags: automation, shower-thoughts
hn_id: 29680269
---

I love automating things, with shell aliases, global hotkeys, IDE snippets etc.

I see this question of have you spent more time automating something, than the time it's saved you?

I've seen this question a lot of times over the years, whenever someone sees me using such a shortcut

> How long did it take for you to build and learn that automation? Was the time you saved from it worth it?

My answer to that is, of course, yes. But the question is a little more nuanced.

_Was the time saved **worth** it?_ Yes.

_Was the time saved **more** than the time you spent in building and learning?_ No.

So, I spent _more_ time, in building and learning the shortcut, than I saved because of the shortcut. This was illustrated well in [this XKCD comic](https://xkcd.com/1205/):

![Is it worth the time](https://imgs.xkcd.com/comics/is_it_worth_the_time.png)

This, for most people, makes learning such shortcuts a waste of time. Because, of course, the net time difference is negative. Therein lies the folly.

> Not all five minutes hold the same value.

There are times when I'm working on a critical fix that needs to go out in negative time. I hope to not end up in such situations, but we do. In such situations, saving a few precious seconds can mean a lot.

Consider a hypothetical example, an internal application server is down for whatever reason. I need to SSH into the server to see what's up. Sure, I could go into my notes, search for the long SSH command for this server, SSH into it, then run commands to check logs, and then to restart if needed etc.

But, what if this was a single shell script. Just SSH into that server, print me the logs, and ask me if I want it restarted or not. Just a Y/N answer. I'm quite sure developing such a script would take more time than I'd be saving. However, I'd be spending that time developing this script, when I'm not in a hurry.

I can afford to spend those _ten minutes_ in such a situation, to save _ten seconds_ in a more critical situation. This is what makes it worth it.

But there's an ugly face to this. We should know when some shortcut is _enough_. It's easy to get into the trap of trying to optimize it and make it better and better. This is well represented in [this comic by XKCD](https://xkcd.com/1319/):

![The trap of automation, by XKCD](https://imgs.xkcd.com/comics/automation.png)

Part of the problem is, developers, just like artists, often are never done. There's always a small finishing touch that can be done.

The trick is recognize, and even assume, that you'll be the only user ever of this shortcut. If it works for you, without too many brain cycles, in a critical situation, you're done. Move on.

So, what do I automate? I've written about my automations and workflows quite a bit in the past:

- [Automating with Vim workplace](./2020-01-12-automating-the-vim-workplace.md), [part 2](2020-02-16-automating-the-vim-workplace-2.md), and [part 3](2020-03-15-automating-the-vim-workplace-3.md).
- [The Magic of AutoHotkey](2020-03-01-the-magic-of-autohotkey.md), and [part 2](2020-03-22-the-magic-of-autohotkey-2.md).

Today, I primarily work with macOS, and have come to love Hammerspoon, as an alternative to AutoHotkey on Windows. I intend to write about my Hammerspoon automations as well, soon.

As I always say, _identify, automate, repeat_.
