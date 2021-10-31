---
title: Python's `map` builtin function
tags: python, programming, reference
description: >
    An article with examples and explanations of Python's map builtin function, supplementing the
    official documentation on this topic.
hn_id: 21960757
---

In this article, we'll take a look at Python's stream processing utility function, `map`. This
function can enable us to write powerful list/stream-processing routines that can be easy to read
and understand.

Let's go over the basics first so we have context when talking about them.

## Syntax

Calling `map`:

```python
# From official docs
map(function, iterable, ...)
```

Where

function
:   Called with each item from `iterable`.

iterable
:   Use to take inputs for calling `function`.

*returns*
:   Iterable of return values from calling `function`.

## Working of `map` Function

Here's a run-book for the `map` builtin function:

1. Accepts two arguments, a function (or any callable) and a list (or any sequence) of objects.
1. Call the function once per object in the list, pass the object to the function, and collect the
   return value from each call.
1. Return a generator that will yield the return values as collected by applying above step over and
   over until the list from point 1 is exhausted.

Note that in Python 2, `map` used to return a `list` object. However, in Python 3, it returns a
`map` object which is a generator that lazily processes each item in the list as they are needed. If
you don't want to bother with this difference for now, remember to always wrap the result of a `map`
function with a `list`. The official `2to3` tool handles this automatically.
{: .note }

Let's look at some examples:

```pycon
>>> map(str, range(5))
<map object at 0x0000000002DCD3C8>
>>> list(map(str, range(5)))
['0', '1', '2', '3', '4']
```

Notice how in the first call to `map`, we get a `map` object show up in the result. In this case,
none of the items in `range(5)` have been processed by `str`. But when we wrap it in `list` the next
time, we get the list of all processed items.

We can also pass in lambda functions just fine.

```pycon
>>> list(map(lambda x: x**2, range(5)))
[0, 1, 4, 9, 16]
```

But don't do that, that's silly. We'll see why later down in this article, but, put simply,
*comprehensions are almost always better than a map+lambda combination*.

Additionally, `map` can also take more than one sequence in it's arguments. In that case, the items
produced by each of the other sequence make up for additional arguments for the given function.

Consider the following call to `map`:

```python
list(map(sum, [1, 2, 3], [7, 8, 9], [100, 200, 300]))
```

This will call the given `sum` function three times,

    sum(1, 7, 100)
    sum(2, 8, 200)
    sum(3, 9, 300)

It produces a result list of three items, the three return values of the above three calls to `sum`.

Let's look at some useful ways we can use the `map` function in real world code.

## Using Unbound Methods

If the function we want to call is a *method call* on each object in the given list, we could use
a comprehension or do it with map+lambda like this:

```pycon
>>> protocols = ['http', 'tcp', 'xmpp', 'irc']
>>> [protocol.upper() for protocol in protocols]
['HTTP', 'TCP', 'XMPP', 'IRC']
>>> list(map(lambda protocol: protocol.upper(), protocols))
['HTTP', 'TCP', 'XMPP', 'IRC']
```

But a much simpler way, is to provide the unbound method as the first argument to `map`.

```pycon
>>> list(map(str.upper, protocols))
['HTTP', 'TCP', 'XMPP', 'IRC']
```

The reason this works is because calling unbound method with an instance as the first argument, is
almost the same thing as calling the bound method of that instance. In other words,
`str.upper('http')` is more or less the same as `'http'.upper()`. This is true for any method on any
class (even `classmethod`s if you have a list of classes).

## More Types of Sequences

Pass in sets, dictionaries (also `mydict.get` as function), file objects, a string (`map(ord,
'abc')`) etc.

The second argument to `map` can be any sequence data type, doesn't have to be a `list`. Here's some
types that are quite useful with `map`:

1. Sets (function called with each *item* in set)
1. Dictionaries (function called with each *key* in the dictionary)
1. Files (function called with each *line* in the open file object)
1. Strings (function called with each *character* in the string)

We can use dictionaries as the sequence to run a function over each *key* in the dictionary.
Additionally, we can use the `.items` or `.values` to have `map` run the function over each `(key,
value)` tuple or just the values respectively.

```pycon
>>> numbers = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
>>> list(map(len, numbers))
[3, 3, 5, 4]
>>> list(map(str, numbers.values()))
['1', '2', '3', '4']
>>> list(map(repr, numbers.items()))
["('one', 1)", "('two', 2)", "('three', 3)", "('four', 4)"]
```

We can use `map` to transform the lines of a file as we are reading over it. This is actually very
useful to do some small preprocessing on the lines, like removing trailing white space.

```python
with open('contents.txt') as open_file:
    for line in map(str.rstrip, open_file):
        pass
```

We can map a function like `ord` (returns the Unicode code point for a single character) over a
string, to get the code points for each character in the string.

```pycon
>>> list(map(ord, 'aluminium'))
[97, 108, 117, 109, 105, 110, 105, 117, 109]
```

## Dictionaries as Transformers

This is another neat trick where we have a dictionary and a list of some *keys*. We use `map` to
transform the list of keys to a list of values, referring to the dictionary.

```pycon
>>> numbers = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
>>> keys = ['three', 'four', 'two', 'five', 'four', 'two']
>>> list(map(numbers.get, keys))
[3, 4, 2, None, 4, 2]
```

Notice that when faced with a key like `'five'` that doesn't exist in the dictionary, we get `None`,
which is how the `dict.get` behaves.

Note that in this call to `map`, we are passing a *bound* method, `numbers.get`. This is essentially
the `dict.get` unbound method, which has been bound to the `dict` instance we are calling `numbers`.
{: .note }

## Infinite Sequences

Since `map` is lazy from Python 3, it can work with infinite sequences just fine. For our purposes,
let's create a generator that will generate positive even numbers from zero to infinity:

```pycon
>>> def positive_evens():
...     n = 0
...     while True:
...         yield n
...         n += 2
```

Since this generator never stops by itself, calling `list(positive_evens())` will never return. So,
we have to put a cap on the amount of data we generate ourselves. Of course, `map` doesn't care.

```pycon
>>> for e in positive_evens():
...     if e > 3:
...         break
...     print(e)
...
0
2
>>> import math
>>> for e in map(math.sqrt, positive_evens()):
...     if e > 3:
...         break
...     print(e)
...
0.0
1.4142135623730951
2.0
2.449489742783178
2.8284271247461903
```

The `map` function doesn't care that the generator we passed in is never ending. It only processes
as many items as the `for` loop requests.

Be careful with infinite generators though, it's very easy to end up in an infinite loop situation.
{: .note }

## Side Effect Operations

The `map` function is best used as a *transformation* done to each item in a sequence. In this
sense, the function that's passed in is usually a pure function. Passing in functions that are
purely intended for side effects (like `print`, `log.debug` etc.) is in bad taste (opinion alert!).

This is mostly because of two reasons. First, we'll have to pass the return value of `map` to `list`
to get our `print` calls to run. Second, we'll then have a list of `None`s that's just a sad waste.

```pycon
>>> list(map(print, protocols))
http
tcp
xmpp
irc
[None, None, None, None]
```

The better way to do this is to just use a `for` loop and make the intention clear. The intention is
to do something *with* each item in the sequence. Not to do something *to* each item in the sequence
and collect their return value.

```pycon
>>> for protocol in protocols:
...     print(protocol)
http
tcp
xmpp
irc
```

Much better.

## String join

Since we can use bound methods with `map` as well, we can pass in methods bound string methods like
`str.join`:

```pycon
>>> planets = {'one': 'un', 'two': 'deux', 'three': 'trois'}
>>> list(map(':'.join, planets.items()))
['one:un', 'two:deux', 'three:trois']
```

## Case Against `lambda`+`map`

Since `map` accepts any callable, it can be tempting to use `lambda` functions inside `map`. This is
almost always bad taste, and usually, comprehensions (along with `zip`) offer a more readable
alternative.

Consider the following use of `map` with `lambda`:

```pycon
>>> list(map(lambda x: x * 2, range(5)))
[0, 2, 4, 6, 8]
```

Now compare that with the same thing done with a comprehension:

```pycon
>>> [x * 2 for x in range(5)]
[0, 2, 4, 6, 8]
```

Now, of course we can use comprehensions even if we are not using `lambda` in `map` by just calling
it in the comprehension, true, but in that case, `map` just looks prettier ;).

```pycon
>>> [ord(c) for c in 'hello']
[104, 101, 108, 108, 111]
>>> list(map(ord, 'hello'))
[104, 101, 108, 108, 111]
```

In fact, any call to `map` can be translated to a comprehension:

```python
map(function, iterable, ...)
# same as
(function(*vals) for vals in zip(iterable, ...))
```

But that doesn't mean `map` is not useful. We just have to pick the right option depending on the
need.

## Conclusion

The `map` function is powerful builtin, but should be used with care. If you find yourself nesting
several different calls to `map`, you may want to rethink that strategy since it quickly becomes
unreadable.

But when it produces clear-to-understand code, `map` can be very useful tool.

Thank you for reading! Do you have any clever examples of using `map`? Share in the comments!