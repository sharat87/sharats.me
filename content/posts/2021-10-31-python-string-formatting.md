---
title: Python string formatting
status: draft
---

Show string formatting from several other languages?
{.note}

## Percentage Style Formatting

Python supports C's `printf`-style formatting using percentage prefixed format specifiers. For example, the format specifier `d` is used for formatting integers, so the expression `'I have %d candies.' % 7` would return the string `'I have 7 candies.'`.

The syntax for this style of formatting follows a structure like the below:

    <string-expression> % <single-format-value-or-tuple-of-multiple-values>

Here's a few examples:

    :::pycon
    >>> 'I have %d candies.' % 7
    'I have 7 candies.'
    >>> 'I am %d and my sister is %d.' % (15, 13)
    'I am 15 and my sister is 13.'

Notice that when there's more than one values for formatting, we provide them as a tuple. But when
it's a single value, we provide the value directly. Of course, if we wanted, we *could* use a tuple
even when there's a single value:

    :::pycon
    >>> 'I have %d candies.' % (7, )
    'I have 7 candies.'

So far, we've been looking at the `%d` specifier, but additionally we have `%f` for floating point
values, `%s` for strings etc. The full list can be seen at [the official
documentation](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting) on
this topic.

Note that giving a value of the wrong type to a specifier *may* raise an exception. It is usually a
good idea to ensure the format specifier's type matches the values being passed in. The following
table illustrates this point where we try to format a few specifiers with values of different types:

| String | `42`          | `3.141`      | `'moon'`    | `'84'`      |
| ------ | ------------- | ------------ | ----------- | ----------- |
| `'%d'` | `'42'`        | `'3'`        | `TypeError` | `TypeError` |
| `'%f'` | `'42.000000'` | `'3.141000'` | `TypeError` | `TypeError` |
| `'%s'` | `'42'`        | `'3.141'`    | `'moon'`    | `'84'`      |
| `'%r'` | `'42'`        | `'3.141'`    | `"'moon'"`  | `"'84'"`    |

We can see that the format specifiers *try* to interpret the given value in their type.

- format modifiers like `%03d`
- named specifiers
- implemented with `__mod__`

## New Style Formatting (Using `str.format`)

- The `format` function (including supporting custom objects on it, f-strings)

## The `f`-strings

- can be used with raw string modifier as well

