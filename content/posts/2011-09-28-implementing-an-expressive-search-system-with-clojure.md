---
title: Implementing an expressive search system with clojure
tags: clojure
---

## Backstory

I have recently learned [Clojure][] and its the first time I've been exposed to
lisp and the code-as-data way of life. I was eager to use Clojure to make an
app, any app, a simple silly personal tool to help me out with a tedious task.

[Clojure]: http://clojure.org

One such tool I created was [classypants][]. Its a small swing based GUI tool
that helps one to make sense out of the values of `PATH` like variables. The
values of these variables are a list of paths of files/directories joined with
`:` in \*nix systems and `;` on windows. Have you ever seen `CLASSPATH` entries
that have ~100 jars/directories in it? Even if these values have just 20 items,
its very hard to make any sense out of it.

[classypants]: http://classypants.sharats.me

Classypants is basically a pretty bare window carrying only 4 top level
controls, one of which is an input box for searching through the entries. That
search is what I want to talk about in this post.

## Superpowers

Initially, the search box was just a filter box. I type some text and the
entries that contain that text and shown, rest hidden. This quickly became
annoying as I wanted to search for entries with `jaxb` and `jar`, which was not
possible with the then implementation.

The implementation of the search I have today can do much more than even that.
Its a powerful query language at work, using which we can filter entries that
point to non-existing files, entries that point to directories that contain a
said file and other weirdos.

## How is it done?

I want to share how I went about evolving the search functionality. Let's talk
about one function here,

```clojure
(defn matches?
  [search-str entry]
  (-> resource
    (.indexOf search-str)
    (not= -1)))
```

This is the first incarnation of the search implementation. It just checks if
the given `search-str` is present inside the `entry`.

That is nice and useful. But we want more power. We want a nice minimal query
language to describe what we want to find, and it should be easy to remember.
Lets work on negation of search results first, thinking up the simplest of
syntaxes,

```clojure
not resource
```

should match entries that do *not* contain `resource`. This doesn't look good,
as it might also mean to search for entries that contain `not` or `resource`. We
need some sugar to identify the `not` part as a directive that modifies how the
search is done. Lets try again,

```clojure
:not resource
```

Ah, the `:` in from of `not` gives it the special behaviour we need. Don't worry
too much about why the syntax isn't `not: resource` or something else, it will
become clear in a moment, if it hasn't already. Now that we have a search
syntax, its time to get it work. Imagine a function, `digest`, which takes a
search string and returns a *function*, which takes an entry and tells if its a
match or not. I suck at writing, read that again.

Essentially, `(digest ":not resource")` should return a function, which more or
less works like

```clojure
(fn [entry]
  (not (matches? "resource" entry)))
```

We see if there is a match, and `not` its result. Lets try writing the `digest`
function,

```clojure
(defn digest
  [search-str]
  (read-string (str "(" search-str ")")))
```

What we do above is wrap the `search-str` in parenthesis and read it into a
Clojure `list`. Lets try out our function in the REPL.

```clojure
user=> (digest ":not resource")
(:not resource)
```
Yep, just what we expected. Now, lets take this further ahead

```clojure
(defn digest
  [search-str]
  (let [spec (read-string (str "(" search-str ")"))]
    (cond
      (= (first spec) :not) (fn [e]
                              (not (matches? (nth spec 1) e))))))
```
