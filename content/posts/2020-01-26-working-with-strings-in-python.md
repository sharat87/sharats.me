---
title: Working with Strings in Python
tags: python, programming, reference, tutorial
description: >
    Everything you need handy as a quick reference when working with strings in Python. A complement
    to the official documentation.
---

This article will be a practical rundown of working with strings in Python, made up of things I
constantly forget and have to look up on how to do. I hope it will serve as a super-quick reference
for me as well as for anybody else who stumbles here.

This document is not intended for beginners to Python. Although you can still get something out of
it, it's best suited for intermediate Python programmers. I tried to illustrate the concepts in a
crisp manner with minimum carry-over context from one section to the next.

[TOC]

## Defining Strings

### Single and Double Quoted Strings

We'll refer to strings delimited by the `'` character as single quoted strings and those delimited
by `"` as double quoted strings.

They are identical in all respects, except that single quote needs to be escaped in single quoted
strings and double quote needs to be escaped in double quoted strings.

They cannot span multiple lines. A string's ending quote character must appear in the same line as
it begins. This can be worked around by using a `\` character at the end of the line. For example:

```python
text = 'abc\
def'
print(text)
```

This will print:

    abc
    def

But it's best to avoid breaking using `\` to break strings into multiple lines. It's not pretty and
there's better way to do it. Especially [auto-concatenated strings](#auto-concatenated-strings)
(discussed below).

### Tripled Quoted Strings

Tripled quoted strings are a syntax for defining multi-line strings. There's no practical difference
between defining strings with `'''` and `"""`.

In practice, this syntax is commonly used for one of the following:

1. [Docstrings](#docstrings) (discussed below), for writing documentation for classes/functions.
1. Module level constant strings that contain long multi-line content. Can be used for small HTML
   templates that are stored inline or complex SQL queries, long regular expression patterns etc.
1. An *approximation* for multi-line comments. Python doesn't have multi-line comments (like `/*`
   and `*/` in C-like languages). Wrapping whole code blocks with tripled quotes can turn it into a
   pseudo-comment. I personally discourage this, but it's nonetheless used in real-world code.

The string created when using tripled quoted strings will contain *everything* between the tripled
quotes. This includes any indentation present due to Python block-style formatting. For example:

```python {"linenos": true}
def make_story():
    text = '''
    Once upon a time, there was a planet.
    Suddenly, it named itself Earth.
    And it hoped to live happily ever after.
    '''

    return text


print(repr(make_story()))
```

This will produce the following output:

    '\n    Once upon a time, there was a planet.\n    Suddenly, it named itself Earth.\n    And it hoped to live happily ever after.\n    '

There's three things to note in the string defined in this function:

1. It starts with a newline character, the one that comes right after the opening `'''` on line 2.
    - This particular point can be easily addressed by adding a `\` right after the opening `'''`.
1. Each line, except for the first, starts with four spaces, because of the indentation of the
   `make_story` function.
    - The [`textwrap.dedent`][dedent] function from standard library can help deal with this.
      Details in the next paragraph.
1. It ends with a newline character and the four spaces from the line 6.
    - Calling `.strip` (or `.rstrip`) on the string can do this.

Considering the above three points, we rewrite the previous code fragment as:

```python {"linenos": true}
import textwrap

def make_story():
    text = textwrap.dedent('''\
    Once upon a time, there was a planet.
    Suddenly, it named itself Earth.
    And it hoped to live happily ever after.
    '''.rstrip())

    return text
```

Note that it is important to use `.rstrip` here, and not `.strip`. The reason is that `.strip` will
remove the whitespace before `Once...` line and so the first line in the string won't have any
indentation. Now the documentation of `textwrap.dedent` says:

> Remove any common leading whitespace from every line in text.

But since our first line doesn't have the indentation anymore, there's no *common* leading
whitespace in `text`. So, this function won't remove the indentation. Another option would be to do
`dedent` first, and then call `.strip` on the result of `dedent`.

The output of this program would be:

    'Once upon a time, there was a planet.\nSuddenly, it named itself Earth.\nAnd it hoped to live happily ever after.'

### Escape Characters

Backslash based escape characters behave exactly the same way in strings defined with any quote
type.

Following is a list of *commonly used* escape characters. This list is **not exhaustive**.

| Escape sequence        | Result                                                                        |
| ---------------------- | ----------------------------------------------------------------------------- |
| `'\'` (at end of line) | String definition is continued to next line                                   |
| `'\n'`                 | Newline character                                                             |
| `'\\'`                 | Literal backslash character                                                   |
| `'\''`                 | Single quote character, useful in single quoted strings, but works everywhere |
| `"\""`                 | Double quote character, useful in double quoted strings, but works everywhere |
| `'\xhh'`               | Character by hex value given by the `hh` part                                 |

Regarding escaping quote characters:

1. Single quotes don't *have to* be escaped in double quote strings, but it's not an error to do so.
1. Double quotes don't *have to* be escaped in single quote strings, but it's not an error to do so.
1. Neither quotes *have to* be escaped in tripled quote strings, but it's not an error to do so.

In tripled quote strings, the delimiters **cannot be escaped** to become part of the string. For
example, a `'''` sequence cannot be part of the string when the string is defined with `'''`. But it
may be part of the string, when it's defined with `"` or `"""`. This behaviour cannot be escaped.

## Auto-concatenated Strings

Python has a nice compiler level feature to auto-concatenate *literal* strings that are next to each
other (or more correctly, forming a single expressions). Take a look at an example to illustrate the
point:

```python {"linenos": true}
query = (
    'SELECT * FROM employees'
    '  WHERE name = ?'
)

print(query)
```

The string `query` is defined as two parts, each on lines 2 and 3. These two strings will be
concatenated automatically at compile-time. The output of the above program would be:

    SELECT * FROM employees  WHERE name = ?

Things to note regarding this behaviour:

1. The strings don't have any operator between them, like `+` or `,` or something else.
1. This works only with *string literals*, it won't work when applied to variables.
1. This is a compile-time feature, and so is more performant than string concatenation using the `+`
   operator.
1. The multiple string literals should be part of the same expression. So, if we are writing them on
   multiple lines, they have to wrapped in parentheses or we should use the `\` character to tell
   Python to treat multiple lines as a single expression.
1. Works with combinations of ordinary strings, raw strings, format strings and any combinations of
   them together.

Thanks to this feature, there's almost never a reason to define long string constants by
concatenating several strings.

## Raw Strings

Python's raw strings' syntax is a small variation that disables the escaping behaviour of the `\`
character. A string is treated as a raw string if the starting delimiter quote is prefixed with a
`r` (or `R`) character.

The following expressions create *equal* (as defined by `==` operator) string:

| Unadorned string | Raw string     |
| ---------------- | -------------- |
| `'abc'`          | `r'abc'`       |
| `'abc\ndef'`     | *not possible* |
| `'abc\\ndef'`    | `r'abc\ndef'`  |

In other words, the special escaping behaviour of `\` character cannot be used in raw strings. This
is useful when you have a lot of `\\` in your unadorned string. Such a string's definition can be
much simpler if using raw strings.

Points to note regarding raw strings:

1. Can be used with single, double or tripled quotes.
1. The actual string object created is no different from the one when using unadorned string syntax.
   It is just a syntax-level convenience.
1. Delimiter quotes cannot be included in raw strings. In other words, single quotes cannot be a
   part of raw single quote strings. For example, `r'abc\'def'` gives the string `"abc\\'def"`. That
   is, the string will contain one backslash, and one single quote, essentially it will be exactly
   as it looks like in the definition.
1. Cannot be defined to end with a single `\`. The expression `r'abc\'` will raise a `SyntaxError`.
   The expression `r'abc\\'` will end with two backslash characters.

The limitations above can be worked around by using raw and ordinary strings together.

Most commonly useful scenarios for raw strings:

1. Regular expression patterns, to be used with the [`re`][re] module.
1. Windows style file paths, where the separator is the backslash character. Note that the `open`
   function works fine even with forward slashes on Windows, so this is *generally* not needed.
1. SQL queries, especially when defined with tripled quotes as module level constants.

## Concatenation

The `+` operator can be used to concatenate two strings. This will create a new string object which
is the result of the concatenation (`str` objects are immutable in Python).

If there's several strings being concatenated, using the `+` operator may not be the best way to do
this. For example, consider the following snippet of code:

```python
text = ''

for i in range(4):
    text += 'we have %r\n' % i

print(text)
```

When run, it produces the following output:

    we have 0
    we have 1
    we have 2
    we have 3

However, using the `+` operator here means that intermediate string objects are created at every
concatenation operation. This is needless memory allocation since these intermediate string objects
are never used, and are ready for garbage collection rather quickly. For situations like this,
there's better options than concatenating strings using `+` operator.

**One option** is to use a list and then pass it to `''.join` method to concatenate them all in one
go. Using this option in the above code snippet, we get:

```python
fragments = []

for i in range(4):
    fragments.append('we have %r\n' % i)

text = ''.join(fragments)
print(text)
```

Additionally, in this case, we could've used `'\n'.join` instead and avoid the trailing newline in
`text` (*if* that's what is desired, don't do it just because we can).

```python
lines = []

for i in range(4):
    lines.append('we have %r' % i)

text = '\n'.join(lines)
print(text)
```

**Another option** is to use [`io.StringIO`][StringIO] which is a file-like, in-memory, string
buffer that you can `.write` string content to and then turn it into a single string object when
done. Rewriting the above code snippet to use this option:

```python
import io

buffer = io.StringIO()
for i in range(4):
    buffer.write('we have %r\n' % i)
text = buffer.getvalue()
print(text)
```

Both solutions are better than concatenating strings with `+` operator, but if you're just
concatenating two or three strings, it's probably simpler to just use `+` and move on. Premature
optimisation is the root of all evil.

## Splitting

Python strings have the [`.split`][str.split] method that can be used to split strings into list of
tokens or parts. There's three things to this method to understand:

**First**, it takes a separator argument, which can be a string of any length.

```python
print('a,b,c,d'.split(','))
print('a,b;c,d'.split(';'))
print('a b c d'.split(' '))
print('a,,b,,,'.split(','))
```

This will produce the following output:

```python
['a', 'b', 'c', 'd']
['a,b', 'c,d']
['a', 'b', 'c', 'd']
['a', '', 'b', '', '', '']
```

Note that adjoining separators will produce empty strings in the returned list.

**Second**, not passing a value for the separator (or passing `None`) will split the string over
*whitespace*. Note that this is not the same as splitting with the space character (`' '`). Consider
the following examples:

| Expression                   | Result                |
| ---------------------------- | --------------------- |
| `'a b c'.split()`            | `['a', 'b', 'c']`     |
| `'a    b         c'.split()` | `['a', 'b', 'c']`     |
| `'a\tb\nc'.split()`          | `['a', 'b', 'c']`     |
| `'a b c  '.split()`          | `['a', 'b', 'c', '']` |
| `'a b c  '.strip().split()`  | `['a', 'b', 'c']`     |

If you're familiar with regular expressions, then this splitting over whitespace is similar to
splitting over non-overlapping matches of the pattern `\s+`.

**Third**, there is a second argument, which is the maximum number of times the string will be cut
with the given separator (or whitespace). Thus, if we give `1` in the second argument, the result
string will contain *at most* two elements. Of course, not providing any second argument will mean
the string will be split at all occurrences of the separator.

| Expression                             | Result                 |
| -------------------------------------- | ---------------------- |
| `'a,b,c,d'.split(',', 2)`              | `['a', 'b', 'c,d']`    |
| `'a,b,c,d'.split(',', 10)`             | `['a', 'b', 'c', 'd']` |
| `'hello'.split(',', 10)`               | `['hello']`            |
| `'a    b         c'.split(maxsplit=1)` | `['a', 'b         c']` |

### The `.splitlines` Method

The [`.splitlines`][str.splitlines] method splits the strings into a list of lines. This method is a
better version of just doing `.split('\n')` since it handles many of the nasty end-of-line
differences. For example, if your string contains `'\r\n'` at the end of each line, then doing a
`.split('\n')` will leave dangling `'\r'` characters at end of each line. This is handled well by
the `.splitlines` method. The [official documentation][str.splitlines] has a list of separators
this method splits by, which I won't repeat here.

| Expression                     | Result                 |
| ------------------------------ | ---------------------- |
| `'a\nb\rc\r\nd'.splitlines()`  | `['a', 'b', 'c', 'd']` |
| `'a   b\rc\r\nd'.splitlines()` | `['a   b', 'c', 'd']`  |

## Substring Check

To check if a string is wholly contained in another string, the `in` operator should be used. Note
that this operator is case-sensitive. If case-insensitivity is needed, the easiest option is to just
call `.casefold` (which is especially designed for this purpose) on both the strings.

```python
needle = 'back'
haystack = 'Going back and forth all the time.'
print(needle in haystack)
```

This would print `True`, since the string `'back'` occurs in `haystack`. Note the intent here, for
example, consider the following example:

```python
needle = 'back'
haystack = 'Forwards is easier than backwards.'
print(needle in haystack)
```

This would again print `True`, but the intent seems to be to look for the *word "back"*. In that
case, we'd expect `False` here and `True` in the previous example (since *back* is not a separate
work in the second example). Here again, a simple solution is to call `.split` on the `haystack`
string before the `in` operator check. The idea is that we'd get a list of words out of `haystack`
and we check if needle occurs in the list.

```python
needle = 'back'
haystack = 'Forwards is easier than backwards.'
print(needle in haystack.split())
```

This prints out `False`. This isn't anywhere near a foolproof word searching system, but does get
you a step ahead.

### Prefix and Suffix Check

We have the `.startswith` and `.endswith` methods on strings if we want to check if a string is not
just *in* another string, but more specifically, if it starts/ends with it.

```pycon
>>> 'the' in 'Hello there'
True
>>> 'Hello there'.startswith('he')
False
>>> 'Hello there'.endswith('ere')
True
>>> 'Hello there'.lower().startswith('he')
True
```

Additionally, there's a useful twist to these two functions. Instead of a single string as argument,
they can accept a `tuple` of strings where it check if the original strings starts/ends with **any**
of the strings in the tuple. Check out the following examples:

```pycon
>>> 'Hello there'.startswith(('He', 'he'))
True
>>> 'hello there'.startswith(('garbage from outer space', 'He', 'he'))
True
```

A less obvious fact here is that the original string *may* be shorter than the string being passed
to `.startswith`/`.endswith`. This sounds like a nobrainer, but there's one scenario where it's
particularly nice.

Consider a situation where we want to check if the first character of a string is, say, `'A'`. One
option to do this is `haystack[0] == 'A'`. But this runs the risk that if the `haystack = ''`, then
`haystack[0]` will raise an `IndexError`, where we just wanted `False`. If we did
`haystack.startswith('A')`, we'd get `False` if haystack is empty.

### Regular Expressions Check

Regular expressions are a much larger topic than can be fit under a third level header (may be a
future article). So we'll just cover the substring checking part using regular expressions (in
obviously limited scope).

All regex (regular expression) operations in Python start from the `re` module. There's no special
syntax for defining regex patterns like there is in JavaScript. Patterns are instead written as
strings and the `re` module knows to interpret them as regex patterns.

For our purpose of substring checking, the `re` module provides the [`.search`][re.search] function
that takes a regex pattern, the haystack string and optionally, any flags for the pattern.

```python
import re
print(re.search('the', 'Hello there'))
print(re.search('he', 'Hello there'))
print(re.search('he', 'Hello there', flags=re.IGNORECASE))
print(re.search('hola', 'Hello there'))
```

This would produce the following output:

    <re.Match object; span=(6, 9), match='the'>
    <re.Match object; span=(7, 9), match='he'>
    <re.Match object; span=(0, 2), match='He'>
    None

A minor point to note here is that the return value is not of *boolean* type. We get an
[`re.Match`][re.Match] object if there is a *successful match*, else we get `None`. This is usually
a minor concern, because the match objects are *truth-y* and `None` is *false-y*. So, we can pretend
it returns a *boolean* value if we need to.

When using the `re.search` function this way, the [`re.escape`][re.escape] function might also come
in handy.  This function will escape any special characters in the give string. Special here means
having special behaviour in the context of being a regex pattern.

For example, if the needle is user input and we want to search our haystack such that the needle is
at the end of an English sentence, we'd do something like:

```python
re.search(needle + '[.!?:]', haystack)
```

But this runs the risk of `needle` having regex special characters like `.*` and that would match
everything, which is *probably* not what we want. In this case, it's best to wrap the `needle` in
`re.escape` and *then* concatenate the pattern with end-of-sentence markers.

```python
re.search(re.escape(needle) + '[.!?:]', haystack)
```

As always, please think twice before using regular expressions to solve a problem, and if you do, if
the pattern is longer than five or six characters, please make use of `re.VERBOSE` and add comments
to your pattern. You'll thank yourself later.

## Learning About the Contents

Python's strings have some nice methods to quickly check some facts about it's contents. Here's a
rundown of such methods:

| Method                             | Returns `True` if                                                           | On empty string |
| ---------------------------------- | --------------------------------------------------------------------------- | --------------- |
| [`isalnum`][str.isalnum]           | all characters are alphanumeric                                             | `False`         |
| [`isalpha`][str.isalpha]           | all characters are alphabetic                                               | `False`         |
| [`isascii`][str.isascii]           | all characters are within ASCII range                                       | `True`          |
| [`isdecimal`][str.isdecimal]       | all characters are decimal characters                                       | `False`         |
| [`isdigit`][str.isdigit]           | all characters are digits                                                   | `False`         |
| [`isidentifier`][str.isidentifier] | string can be a valid Python identifier                                     | `False`         |
| [`islower`][str.islower]           | has at least one *cased* character and they are all in lower case           | `False`         |
| [`isnumeric`][str.isnumeric]       | all characters are numeric characters                                       | `False`         |
| [`isprintable`][str.isprintable]   | all characters are printable                                                | `True`          |
| [`isspace`][str.isspace]           | all characters are whitespace                                               | `False`         |
| [`istitle`][str.istitle]           | string is title-cased, *i.e.,* all words start with an upper case character | `False`         |
| [`isupper`][str.isupper]           | has at least one *cased* character and they are all in upper case           | `False`         |

Please use the links to official documentation in the above table to learn more about them. I won't
be repeating those details here.

### Numeric Checks

You might've noticed that we have three different methods that all sound awfully similar to each
other: `isdecimal`, `isdigit` and `isnumeric`. The official documentation regarding the difference
between these three wasn't very helpful for me so I'll try explain it here.

**Firstly**, `isdecimal` will consider any character that can be used to build a number in the
10-decimal system as `True`. That means it will give `True` for the `0` through `9` digits.
Additionally, it will also give `True` for characters that can be used for similar purpose in *other
languages*. For example, the numbers from Unicode range 3174 to 3183 are of a south Indian language
called Telugu (my mother tongue). The `isdecimal` method returns `True` for these characters as
well. However, note that it is not true for Roman numerals since they can't *technically* be used to
construct 10-decimal numbers.

```pycon
>>> # Arabic Numbers
>>> ''.join(chr(i) for i in range(48, 58))
'0123456789'
>>> _.isdecimal()
True
>>>
>>> # Telugu Numbers
>>> ''.join(chr(i) for i in range(3174, 3184))
'౦౧౨౩౪౫౬౭౮౯'
>>> _.isdecimal()
True
```

**Secondly**, `isdigit` gives `True` for any character that *looks like* a **digit**, of any
language.  So, this includes any character that is `True`-ed by `isdecimal`. Additionally, this
includes characters like `¹`, `²`, `³`, *etc.,* as well as `①`, `②`, `③`. Notice that fraction
characters are not considered as *digits*.

**Thirdly**, `isnumeric` gives `True` for any character that is *numeric* in nature. So, this
includes any character that is `True`-ed by `isdigit`. Additionally, this will give `True` for
fraction characters such as `¼`, `½`, `¾` *etc.*, as well as Roman numbers such as `Ⅰ`, `Ⅱ`, `Ⅲ`,
`Ⅳ`, even `Ⅹ`, `Ⅼ`, `Ⅽ`, `Ⅾ`, `Ⅿ` (these are not ordinary alphabets, they are Unicode Roman number
characters) *etc.*

This follows a neat fact regarding the character sets `True`-ed by the three methods: `isdecimal`
&sub; `isdigit` &sub; `isnumeric`.

## Transformations

This section is about methods that return a new string, which is the result of some transformation
applied to the original string. Since strings in Python are immutable, transformations always return
a new string object. The original string is, always, obviously, left untouched.

Here's a few commonly used transformation methods (this list is intentionally non-exhaustive):

| Method                          | Transformation                                                                                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [`.strip`][str.strip]           | Strips *whitespace* (or characters from the string in first argument) at the start and end of the string.  |
| [`.lstrip`][str.lstrip]         | Strips *whitespace* (or characters from the string in first argument) only at the start of the string.     |
| [`.rstrip`][str.rstrip]         | Strips *whitespace* (or characters from the string in first argument) only at the end of the string.       |
| [`.lower`][str.lower]           | All cased characters are converted to lower case, unless they are already in lower case.                   |
| [`.upper`][str.upper]           | All cased characters are converted to upper case, unless they are already in upper case.                   |
| [`.capitalize`][str.capitalize] | The first letter is upper-cased and the rest are lower-cased.                                              |
| [`.title`][str.title]           | The first letter in each word in the string is upper-cased, *and* all others are converted to lower-cased. |

Please use the links to official documentation in the above table to learn more about them. I won't
be repeating those details here. The official documentation refers to more methods on strings that I
suggest skimming over. I happened to reinvent the wheel with transforming strings because I didn't
know Python already provided a method for what I needed.

## String Formatting

String formatting in Python comes majorly in two flavors. **First** is the (now old) `printf`-style
formatting that uses typed control characters prefixed with `%`, similar to the `printf` (more like
`sprintf`) function in C. **Second** is the new `format` builtin function and the accompanying
`str.format` method that is more suited to Python's dynamic typing, and arguably, is much easier to
use.

Python's formatting capabilities are quite vast and powerful, warranting a whole separate article. I
intend to do that some time in the coming weeks. Until then, the official documentation on
[`printf`-style
formatting](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting) and the
[format function](https://docs.python.org/3/library/functions.html#format) should serve you well.

## Docstrings

Docstrings are strings that serve as documentation for Python's modules, functions and classes.
There's nothing special in the syntax of these strings per se, but their uniqueness is more due to
where they are positioned in a Python program.

Consider the following function with a docstring on line 2

```python {"linenos": true}
def triple(n):
    """Triples the given number and returns the result."""
    return n * 3


print(triple(4))
```

The string defined on line 2 in this program is not assigned to any variable. On the face of it, it
appears pointless to create a string and just discard it. However, in this case, the fact that this
string literal is the first expression in the function definition, makes it a docstring. What that
means is that the contents of this string are understood to be a human readable help text regarding
the usage of this function.

It also doesn't have to be a string defined with `"""`. It may be using single quotes, double quotes
or any other crazy variation we saw above. But, don't do that. It's usually a best practice to write
docstrings with `"""`, and I strongly suggest (and even beg) that you stick to using `"""` for
docstrings. Please.

It's also not *entirely* true that this string is not assigned to a variable. Docstrings are saved
to the `.__doc__` attribute of the function (or whatever object) they are documenting. In our
example above, we can get the docstring from `triple.__doc__`. But it's usually more practical to
call the `help` function to read the docstring.

For classes, the docstring should be the first expression inside the class body, positioned
similarly to that of a function. For modules, the docstring should be the first expression in the
module (even before any imports).

A minor note regarding docstrings regarding the formatting of their content is to use [ReST][rst]
(also called **reStructuredText**). It is not strictly required, but I suggest you do so, in the
event that you choose to generate HTML help pages from your docstrings, you'll be glad you wrote
them in ReST.

## Conclusion

It's hard to imagine a Python program that doesn't have something to do with strings. As such, we
have been provided with a lot of utilities within the standard distribution for working with
strings. Even in an article of this size, I couldn't be exhaustive. As always, Python's official
documentation is unreal good. It pays to occasionally open a random page and skim over it.


[dedent]: https://docs.python.org/3/library/textwrap.html#textwrap.dedent
[re]: https://docs.python.org/3/library/re.html
[re.search]: https://docs.python.org/3/library/re.html#re.search
[re.escape]: https://docs.python.org/3/library/re.html#re.escape
[re.Match]: https://docs.python.org/3/library/re.html#match-objects
[StringIO]: https://docs.python.org/3/library/io.html#io.StringIO
[str.split]: https://docs.python.org/3.8/library/stdtypes.html#str.split
[str.splitlines]: https://docs.python.org/3.8/library/stdtypes.html#str.splitlines
[str.isalnum]: https://docs.python.org/3/library/stdtypes.html#str.isalnum
[str.isalpha]: https://docs.python.org/3/library/stdtypes.html#str.isalpha
[str.isascii]: https://docs.python.org/3/library/stdtypes.html#str.isascii
[str.isdecimal]: https://docs.python.org/3/library/stdtypes.html#str.isdecimal
[str.isdigit]: https://docs.python.org/3/library/stdtypes.html#str.isdigit
[str.isidentifier]: https://docs.python.org/3/library/stdtypes.html#str.isidentifier
[str.islower]: https://docs.python.org/3/library/stdtypes.html#str.islower
[str.isnumeric]: https://docs.python.org/3/library/stdtypes.html#str.isnumeric
[str.isprintable]: https://docs.python.org/3/library/stdtypes.html#str.isprintable
[str.isspace]: https://docs.python.org/3/library/stdtypes.html#str.isspace
[str.istitle]: https://docs.python.org/3/library/stdtypes.html#str.istitle
[str.isupper]: https://docs.python.org/3/library/stdtypes.html#str.isupper
[str.strip]: https://docs.python.org/3/library/stdtypes.html#str.rstrip
[str.lstrip]: https://docs.python.org/3/library/stdtypes.html#str.lstrip
[str.rstrip]: https://docs.python.org/3/library/stdtypes.html#str.rstrip
[str.lower]: https://docs.python.org/3/library/stdtypes.html#str.lower
[str.upper]: https://docs.python.org/3/library/stdtypes.html#str.upper
[str.capitalize]: https://docs.python.org/3/library/stdtypes.html#str.capitalize
[str.title]: https://docs.python.org/3/library/stdtypes.html#str.title