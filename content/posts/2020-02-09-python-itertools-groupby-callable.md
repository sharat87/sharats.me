---
title: Python's `itertools.groupby` callable
tags: python, tutorial, python-itertools, itertools-groupby
description: The itertools.groupby callable that can be used to group contiguous items in a sequence based on some property of the items.
---

The `groupby` utility from the [`itertools`][itertools] module can be used to group contiguous items in a
sequence based on some property of the items.

Python has several utilities for working with lists and other sequence data types. In addition to a
lot of such utilities being directly available as builtins (like [`map`][map-article], `filter`,
`zip` etc), the `itertools` module is dedicated to this purpose. In this article, I'll show the
[`groupby`][groupby] callable from this standard library module. I hope to write more in the future
on the other awesome stuff from this module.

[TOC]

## Basic Usage

The point of `itertools.groupby` can be illustrated quite easily by applying to a list of zeroes and
ones, to be grouped by their values. Check out the following example:

```python
import itertools

numbers = [1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0]

for grouping_value, group_items in itertools.groupby(numbers):
    print('By', grouping_value, '->', *group_items)
```

This will produce the following output:

    By 1 -> 1 1 1
    By 0 -> 0 0
    By 1 -> 1
    By 0 -> 0 0 0
    By 1 -> 1
    By 0 -> 0

Now let's look at this, little by little. The `groupby` call takes one or, probably more often, two
arguments:

iterable
:   An iterable (like a list or any other collection). Items in this collection will be grouped.

key (defaults to `None`)
:   A function that is applied to each element from `iterable`, the return values of which are used
    to do the grouping.

*returns*
:   A generator that yields tuples of `(grouping_value, iterable_of_group_elements)` for each group
    that was found.

In the example above, we give the `numbers` list to the `groupby` call which yields six groups (as
can be seen from the six lines of output). Since we haven't provided a value for the `key` argument,
the grouping occurs on the elements themselves.

So now the output should make sense. The first group, where the `grouping_value` is `1` will contain
three elements, the first three `1`s in our list. The next group, where the `grouping_value` is `0`
will contain the next two `0`s in our list. This goes on until the list passed to `groupby` is
exhausted.

It is important to note here that inside the tuples yielded by `groupby`, what we have are iterables
that yield the group's items. They are not lists. More specifically, the tuple contains an object of
type `itertools._grouper`, which is just an iterable over the values in the group. This point is
elaborated in a [section further below](#groups-are-iterables).
{: .note }

## Non-contiguous Groups

This often comes up as a surprise to people new to `itertools.groupby` (it certainly did for me).
The groups created are of contiguous regions only. For example, if we are trying group even and odd
numbers from a collection ordered of numbers, just a call to `groupby` can produce surprising
results:

```python
import itertools

for is_even, number_group in itertools.groupby(range(10), key=lambda x: x % 2 == 0):
    print('Evens:' if is_even else 'Odds:', *number_group)
```

This produces the following (probably unexpected) result:

    Evens: 0
    Odds: 1
    Evens: 2
    Odds: 3
    Evens: 4
    Odds: 5
    Evens: 6
    Odds: 7
    Evens: 8
    Odds: 9

What we would've liked is something like the following:

    Evens: 0 2 4 6 8
    Odds: 1 3 5 7 9

If we search the ever helpful internet for a solution to this "problem", the answer seems to be to
sort the initial list with the same key function and then pass the result to `groupby`. This is how
that would work:

```python
import itertools

def is_even(n):
    return n % 2 == 0


for is_even_val, number_group in itertools.groupby(sorted(range(10), key=is_even), key=is_even):
    print('Evens:' if is_even_val else 'Odds:', *number_group)
```

This produces an output much closer to what we wanted:

    Odds: 1 3 5 7 9
    Evens: 0 2 4 6 8

Now, ignoring the evil of pre-mature optimization, the fact that we are calling the key function
twice might cause terminally serious itches to some developers. One (possibly silly) way around this
is to store the results of the key function right next to the values, as a tuple and then unpack the
values once we're done grouping. This would look like:

    import itertools

    def is_even(n):
        return n % 2 == 0


    numbers = range(10)
    keyed_numbers = [(is_even(n), n) for n in numbers]
    sorted_numbers = sorted(keyed_numbers)

    for is_even_val, pair_group in itertools.groupby(sorted_numbers, key=lambda pair: pair[0]):
        print('Evens:' if is_even_val else 'Odds:', *(pair[1] for pair in pair_group))

This produces the same output as the previous example, but calls the key function (`is_even` in this
example's case) only *once* per item in our list.

Before you attempt the above apparent *solution* to performance issues, prove to yourself that
firstly, you **have a performance issue** and that this piece of code **is at least part of the
reason** for it. Otherwise you're probably just wasting your time.
{: .note }

Since this is arguably more useful, let's create an alternative `groupby` that will sort first and
then call `itertools.groupby`:

```python
import itertools

def sorted_groupby(iterable, key=None):
    yield from itertools.groupby(sorted(iterable, key=key), key=key)
```

We can use this function like:

```python
for is_even_val, number_group in sorted_groupby(range(10), key=lambda x: x % 2 == 0):
    print('Evens:' if is_even_val else 'Odds:', *number_group)
```

This will produce the same output as below:

    Odds: 1 3 5 7 9
    Evens: 0 2 4 6 8

## Groups are Iterables

I have mentioned this earlier in this article, but it's important enough to stress again. The group
collections yielded by the `groupby` call **are not lists**. They are iterables that are rendered
unusable upon yielding the next group. If you need the values, make sure you collect them before
going to the next group.

For example, consider the following snippet:

```python
import itertools
from pprint import pprint

names = ['Arthur', 'Trillian', 'ford', 'zaphod', 'slartibartfast']

by_casing = dict(itertools.groupby(names, key=str.istitle))
pprint(by_casing)
pprint(list(by_casing[True]))
pprint(list(by_casing[False]))
```

This produces the following output:

    {False: <itertools._grouper object at 0x0000000002B6D278>,
     True: <itertools._grouper object at 0x0000000002B6BF28>}
    []
    []

The seemingly strange thing to notice here, is that although `groupby` returned two groupings, their
grouped values are empty (hinted by the two empty lists output). But of course, `groupby` wouldn't
return a group unless there's *at least* one item in the corresponding collection. So, what's going
on?

This is the point I was getting at in the first paragraph of this section. The grouping collections
(the values in the dictionary above) are *de facto* destroyed once we yield another group. So, if we
wanted to construct a dictionary like this, we need to do something like the following:

```python linenos=true
import itertools
from collections import defaultdict
from pprint import pprint

names = ['Arthur', 'Trillian', 'ford', 'zaphod', 'slartibartfast']

by_casing = defaultdict(list)

for is_title, group_names in itertools.groupby(names, key=str.istitle):
    by_casing[is_title].extend(group_names)

pprint(dict(by_casing))
pprint(by_casing[True])
pprint(by_casing[False])
```

This would produce the following output:

```python
{False: ['ford', 'zaphod', 'slartibartfast'], True: ['Arthur', 'Trillian']}
['Arthur', 'Trillian']
['ford', 'zaphod', 'slartibartfast']
```

Just something to keep in mind.

The above snippet of code uses [`collections.defaultdict`][defaultdict]. I haven't written about
this yet, but I intend to, in the near future (most likely within the 21st century).
{: .note }

## A Really Bad DIY Implementation

Let's try and create an implementation of our own version of `groupby`, called `insane_grouper`. It
should have the following characteristics:

1. Take an iterable, and optionally a key function, interpreting like `itertools.groupby`.
1. Group non-contiguous items as a single collections.
1. Return a dictionary of each group's key value as the keys and the group's list of items as the
   values.
    - This is great since it goes well with our point 2 above. For computing non-contiguous groups,
      it is not possible to compute the groups lazily (why? is an exercise for the reader). So,
      might as well return a dictionary with all the groups.

This might look something like the following:

```python linenos=true
import itertools
from collections import defaultdict
from pprint import pprint

def insane_grouper(iterable, key=None):
    groups = defaultdict(list)

    for item in iterable:
        groups[item if key is None else key(item)].append(item)

    return dict(groups)


names = ['Arthur', 'ford', 'zaphod', 'Trillian', 'slartibartfast']
pprint(insane_grouper(names, str.istitle))

pprint(insane_grouper(range(10), lambda x: x % 2 == 0))
```

The output of this snippet is the following:

```python
{False: ['ford', 'zaphod', 'slartibartfast'], True: ['Arthur', 'Trillian']}
{False: [1, 3, 5, 7, 9], True: [0, 2, 4, 6, 8]}
```

## Usage Tips

Here's a few tips and cases where this can be used to quickly compute distinct collections of
objects:

1. A list of dictionaries can be grouped by the value against a particular key present in all (or
   some?) of the dictionaries in the list.
1. The key function can return a tuple. This can be useful where we need to group the items by
   multiple criteria, instead of just one.

## Conclusion

While the default behaviour of `itertools.groupby` may not always be what one expects, it is still
useful. The important point to note is to understand the problem you're solving, consider the tools
at your disposal and choose the right tool for the job. On that note, I'll leave you with another
link to the [`itertools`][itertools] module.


[map-article]: ../python-map-function/
[itertools]: https://docs.python.org/3/library/itertools.html
[groupby]: https://docs.python.org/3/library/itertools.html#itertools.groupby
[defaultdict]: https://docs.python.org/3/library/collections.html#collections.defaultdict
