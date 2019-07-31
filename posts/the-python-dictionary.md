---
title: The Python Dictionary
date: 2017-09-20T07:50:28+05:30
publishDate: 2017-09-29
tags: ['python', 'data-structures']
---

The Python [Dictionary][] is a key--value style data structure that is tightly integrated with the
language syntax and semantics. Understanding them well can help us use them better and investigate
subtle problems more efficiently.

This is my attempt to document this topic in more depth. Though I included a small section about the
syntax and basic usage of dictionaries, it'll be helpful if you have some beginner--intermediate
level experience with Python.

This article is written for Python 3.6 installed via Anaconda on Xubuntu. Here's the platform
details:

    $ python -V
    Python 3.6.1 :: Anaconda custom (64-bit)
    $ uname -isro
    Linux 4.10.0-33-generic x86_64 GNU/Linux

Note: This is not intended as a substitute for official documentation. The official documentation is
a reference and there will be some overlap. This document is intended as a supplement that covers
more depth and practical nuances.

{{% toc %}}

# Introduction

Dictionaries (type `dict`) are a very powerful data structure, not just in Python. They are present
in almost every modern high level language, sometimes called maps, hashes or associative arrays.
Python's syntax for dictionaries inspired the syntax of the JSON serialization format.

Dictionaries are a fundamental part of Python language and integrate tightly with the semantics and
APIs of the standard library. This can be seen in the fact that we have a special syntax just to
create these data structures.

# Usage

## Syntax

As a quick primer, here's the syntax for defining a dictionary:

```python
country_currencies = {
    'India': 'Rupee',
    'Russia': 'Ruble',
    'USA': 'Dollar',
    'Japan': 'Yen',
}
```

## API

Again, we quickly run down the common operations on dictionaries.

```python
# Get the value of a key.
indian_currency = country_currencies['India']

# Set the value of a key.
country_currencies['France'] = 'Euro'

# Delete a key.
del country_currencies['USA']

# Check for presence of a key.
'Russia' in country_currencies

# Get if key present, otherwise return `None`.
# (Takes a second parameter which is returned when key is missing).
country_currencies.get('USA')

# Set only if the key is not already present.
country_currencies.setdefault('France', 'Franc')
```

# Contents

The contents of dictionaries are made up two components. The keys and the values. The keys form the
index using which we can retrieve the values. Each key uniquely identifies a value within the
dictionary.

## Key Types

The keys form the index of the dictionary. In most practical cases, keys tend to be strings. Tuples
are often used as well. In fact, values of any immutable, hashable types can be used as keys.

So, what is a hashable type? The official documentation of the [`__hash__` method][hash] gives the
full detail of what it is and what are considered hashable. Simply put, if passing an object to the
`hash` builtin function doesn't raise an exception, the object is hashable and *can* be used as a
key in a dictionary.

However, in practice, we should avoid using mutable objects as keys (even if they are hashable).
Especially, if mutation changes the hash of the object.

For example, consider the following `User` class.

```python
class User:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
```

Let's inspect the hash values of `User` objects.

```python
>>> ned = User('Ned', 'Stark')
>>> hash(ned)
8784834659087
>>> ned.first_name = 'Robb'
>>> hash(ned)
8784834659087
```

{{% aside %}}
If you try the above code, you might see a different number. That's because Python default hashing
algorithm includes a random salt.
{{% /aside %}}

As seen above, the hash value did not change even though the object was modified. These `User`
objects can be used as keys for a dictionary since they meet the requirement, but it should be kept
in mind that they are mutable.

```python
>>> ned = User('Ned', 'Stark')
>>> d = {ned: 123}
>>> d[ned]
123
>>> ned.first_name = 'Robb'
>>> d[ned]
123
```

If that doesn't seem confusing, try this:

```python
>>> robb = ned
>>> ned = User('Ned', 'Start')
>>> robb.first_name
'Robb'
>>> robb in d  # Robb isn't in our dictionary!
True
>>> ned.first_name
'Ned'
>>> ned in d  # We gave Ned Stark a value right?
False
```

This can quickly cause headaches and hard-to-find problems.

To *fix* this, if someone later decides to customize the hashing of this class by adding the
following method:

```python
    def __hash__(self):
        return hash((self.first_name, self.last_name))
```

Now, the hash of the object changes when we change the `first_name`.

```python
>>> ned = User('Ned', 'Stark')
>>> hash(ned)
4091961891370636651
>>> ned.first_name = 'Robb'
>>> hash(ned)
-7890115541605828979
```

Using these objects as keys can be confusing as well:

```python
>>> ned = User('Ned', 'Stark')
>>> d = {ned: 123}
>>> d[ned]
123
>>> ned.first_name = 'Robb'
>>> d[ned]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: <__main__.User object at 0x7fd60e7c5828>
>>> ned.first_name = 'Ned'
>>> d[ned]
123
```

In essence, using mutable types as keys in a dictionary can lead to confusing results in a fairly
large codebase.

So, to avoid these potential problems, it's best to use numbers, strings or tuples (containing
numbers or strings) as keys for dictionaries. If you **have** to use other types, keep the hashing
semantics in mind and document the reasons well.

## Retrieving Keys

Dictionaries have a [`.keys`][.keys] method that returns an object of type [`dict_keys`][views]
which is an iterable (technically, a *view*) of the keys of the dictionary. Note that this method
used to return an ordinary `list` in Python 2.

```python
>>> countries = country_currencies.keys()
>>> countries
dict_keys(['India', 'Russia', 'USA', 'Japan'])
>>> import collections
>>> isinstance(countries, collections.Iterable)
True
```

Note that the order of the keys is not retained/defined. Don't rely on the order even if they seem
predictable. It might vary across Python implementations and versions even. Use an `OrderedDict`
when ordering is needed. More on this in a later section.

{{% aside %}}
It should be noted that starting in Python 3.6, order of keys *is* preserved. This is an unintended
side affect of using a more efficient `dict` implementation. As such, the Python documentation
explicitly states that this is an implementation detail and should not be relied upon. [Read
more](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep468).
{{% /aside %}}

So, what's special about `dict_keys`, as opposed to a `list`? Look look!

```python
>>> countries
dict_keys(['India', 'Russia', 'USA', 'Japan'])
>>> country_currencies['France'] = 'Euro'
>>> countries
dict_keys(['India', 'Russia', 'USA', 'Japan', 'France'])
```

See? The `dict_keys` object is a *view* of the keys of the original dictionary object. When the
dictionary's keys change, so does the keys view. Of course, we can make a set of currently
available keys by passing it to `set` builtin. This set would be independent of the dictionary.

```python
>>> set(countries)
{'Japan', 'USA', 'Russia', 'India', 'France'}
```

{{% aside %}}
Most people would suggest and use `list` here, instead of `set`. I personally feel a `set` is
semantically more correct since a `list` indicates the contents have a specific ordering and does
not convey that the contents are hashable, immutable, and more importantly, *unique*. A `set` shares
these features of dictionary keys.
{{% /aside %}}

Additionally, the `dict_keys` objects are themselves `set`-like. They implement the [`Set`][set-abc]
abstraction. So, we don't need to convert them to a `set` in order to do set operations on them. For
example, here's an intersection operation:

```python
>>> isinstance(countries, collections.abc.Set)
True
>>> countries & {'India', 'China'}
{'India'}
```

## Using Tuples for Keys

Here's a quick example of using tuples as keys in a dictionary:

```python
>>> data = {
...     ('a', 1): 'a1',
...     ('a', 2): 'a2',
...     ('b', 1): 'b1',
...     ('b', 2): 'b2',
... }
>>> data['a', 2]
'a2'
```

Note that only tuples that contain hashable types (or further such tuples) can be used as keys.
Lists or dictionaries, on the other hand, cannot be used since they are not hashable.

## Retrieving Values

Values are what the keys index. Naturally, values don't have to be unique, unlike keys. There's no
restrictions on what types can be used as values in a dictionary.

We can get a sequence of values in a `dict` with the [`.values`][.values] method. This returns a
[`dict_values`][views] object.

```python
>>> currencies = country_currencies.values()
>>> currencies
dict_values(['Rupee', 'Ruble', 'Dollar', 'Euro', 'Yen'])
>>> type(currencies)
<class 'dict_values'>
>>> isinstance(currencies, collections.abc.Set)
False
```

This is *live* as well!

```python
>>> del country_currencies['France']
>>> currencies
dict_values(['Rupee', 'Ruble', 'Dollar', 'Yen'])
```

This can be passed to `list` to get a list of values. Using `set` here is probably not a good idea
since unlike the keys, values don't have to be unique or hashable.

## Items Collection

Dictionaries also provide a [`.items`][.items] method that returns all the key--value pairs as a
sequence of 2-tuples.

```python
>>> pairs = country_currencies.items()
>>> pairs
dict_items([('India', 'Rupee'), ('Russia', 'Ruble'), ('USA', 'Dollar'), ('Japan', 'Yen')])
```

Again, just like with `.keys` or `.values`, the sequence is *live* and the order of items is not
defined.

The `.items` method is probably mostly used with the `for` statement to loop over the key--value
pairs.

```python
for country, currency in country_currencies:
    print(f"{country}'s currency is {currency}.")
```

{{% aside %}}
The above code uses [f-strings][] introduced in Python 3.6. In older versions of Python, the
`.format` method or the modulo (`%`) operator should be used.

[f-strings]: https://docs.python.org/3.6/reference/lexical_analysis.html#f-strings
{{% /aside %}}

The `dict_items` object also implements the `Set` abstraction.

```python
>>> isinstance(pairs, collections.abc.Set)
True
```

However, the abstraction's methods only work if the dictionary's values are hashable, not just the
keys. So, for the dictionary we are working with, the `pairs` object can be used as a set.

```python
>>> pairs & {('India', 'Rupee'), ('UK', 'Pound')}
{('India', 'Rupee')}
```

But if we try this on a dictionary whose values are not `hash`able, say, lists, then it fails.

```python
>>> number_types = {
...     'even': [2, 4, 6, 8],
...     'odd': [1, 3, 5, 7, 9],
... }
>>> pairs = number_types.items()
>>> pairs
dict_items([('even', [2, 4, 6, 8]), ('odd', [1, 3, 5, 7, 9])])
>>> isinstance(pairs, collections.abc.Set)
True
```

Let's try intersecting this with an empty set.

```python
>>> pairs & set()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
```

As the error says, `list` is not hashable. So, although the `isinstance` tells us that this is a
`Set`, whether it can actually be used as such, depends on it's contents. This is *not incorrect*,
actually, I feel it's just a consequence of Python's dynamic nature.

# Typing

Dictionaries in Python are what I call a *homogeneous* data structure. What that means is that they
are best used by having all the keys be of the same type and similarly for values. This is enforced
in comparable data structures in statically typed languages like Java's `Map` or Haskell's
`HashMap`. But since Python is a dynamic language, such restrictions are not placed. We can have
keys / values of several different types within the same dictionary.

```python
data = {
    'a': 1,
    42: 'yay!',
    ('a', 'b', 2): True,
}
```

This is still a valid dictionary, although an extremely sad and ugly one (totally my opinion :D).

If using homogeneous dictionaries, the type annotations syntax can be used to declare the type
signatures. We use [`typing.Dict`][typing.Dict] for this purpose as illustrated below.

```python
from typing import Dict, Tuple

number_map: Dict[int, int] = {1: 10, 2: 20, 3: 30}
data_map: Dict[Tuple[str, int], str] = {('a', 1): 'a1', ('a', 2): 'a2'}
```

{{% aside %}}
This is new in Python 3.6. Before 3.6, annotations are only supported for function arguments. [Read
more](https://docs.python.org/3/whatsnew/3.6.html#pep-526-syntax-for-variable-annotations).

Additionally, the `typing` module itself is new in Python 3.5. [Read
more](https://docs.python.org/3/whatsnew/3.5.html#whatsnew-pep-484).
{{% /aside %}}

The general structure is `Dict[<key-type>, <value-type>]`. So, `Dict[str, int]` denotes a dictionary
that maps string keys to integer values.

Note that these type annotations are not checked at runtime. They're mere help to IDEs, static
checkers and human readers. Python's dynamic nature is not affected by these annotations.

However, if such type annotations are declared, you could use a static analyzer like [mypy][] to
perform type checks. I won't be discussing that here.

# Creating Dictionaries

There are a few other ways to create dictionaries besides the `{}` syntax. Here's a few of them.

## Calling `dict`

The `dict` callable can be used to create dictionaries from a list of tuples or bypassing the keys
and values as keyword arguments.

```python
>>> dict([('Chromium', 24), ('Phosphorus', 15), ('Silver', 47)])
{'Chromium': 24, 'Phosphorus': 15, 'Silver': 47}
```

This is obviously more convenient than the dictionary syntax *only* if we already have such a list.
If we have the keys and corresponding values in different lists, we can `zip` them up and pass the
result to `dict`.

```python
>>> dict(zip(
...     ['Sulfer', 'Calcium', 'Gold'],  # Keys
...     [16, 20, 79],  # Values
... ))
{'Sulfer': 16, 'Calcium': 20, 'Gold': 79}
```

Of course, we can pass keyword arguments directly to `dict`, in addition to the above even.

```python
>>> dict(dict([('Chromium', 24), ('Phosphorus', 15)]), Sodium=11, Nitrogen=7)
{'Chromium': 24, 'Phosphorus': 15, 'Sodium': 11, 'Nitrogen': 7}
>>> dict(Sodium=11, Nitrogen=7)
{'Sodium': 11, 'Nitrogen': 7}
```

The second form is better written using the Python syntax. That is more natural to a potential
future reader, and, *slightly* faster[^1] as well.

[^1]: I read the proof for this a long time ago, but I don't remember where :).

## Comprehensions

Python 3 (and 2.7) added support for dict comprehensions which are very similar to list
comprehensions, but with a small variation in syntax.

```python
>>> dict((i, i**2) for i in range(5))  # Using the `dict` builtin.
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
>>> {i: i**2 for i in range(5)}  # Using a dict comprehension.
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

The above two examples create the same dictionary. However, as pointed out in [PEP 274][], the dict
comprehension is more succinct and makes the intent clearer.

# Public Appearance

Unsurprisingly, dictionaries pop up in a lot of places in Python. Here's a few ones.

## Keyword Arguments

When defining a function that takes arbitrary keyword arguments, they are passed to the function as
a dictionary.

```python
>>> def construct(**counts):
...     print(counts)
...     print(len(counts), type(counts))
...
>>> construct(a=1, b=2, c=3)
{'a': 1, 'b': 2, 'c': 3}
3 <class 'dict'>
```

Of course, we can pass a dictionary's data as keyword arguments to a function using similar syntax.

```python
>>> kw_args = {'a': 1, 'b': 2, 'c': 3}
>>> construct(**kw_args)
{'a': 1, 'b': 2, 'c': 3}
3 <class 'dict'>
```

## Namespaces

The `globals` builtin function gives a dictionary of all names and their values in the current
global namespace. We can modify this dictionary to define new names or delete existing ones,
although that's probably a bad idea.

```python
>>> len(globals())
25
>>> globals()['x'] = 123
>>> x
123
>>> del globals()['x']
>>> x
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'x' is not defined
```

The `locals` builtin returns a dictionary of names and values from the local scope, for e.g., the
private local scope inside of a function or method.

The `vars` builtin takes an object as an argument and returns the names available as properties on
this objects. Specifically, it returns the `__dict__` property's value of the given object. When
called without any arguments, then it returns names and values from the local scope. In other words,
`vars() is locals()` return `True`.

# Serialization

Dictionaries, being key--value data structures, extend naturally to be stored into key--value
databases and other NoSQL data stores. However, here we'll look at forms of serializing them into
text and binary forms for transmission or for saving to disk.

## JSON

Nowadays, the thought of serializing a python dictionary is usually followed by using the
[`json`][json-mod] module to [`dump`][json.dump] and [`load`][json.load] using the [JSON
format][json]. No surprise since it's extremely convenient and there's quality parsers and writers
for almost every programming language today. The syntax as well, although not too convenient to
write by hand, is still very simple, lightweight and easy to read. It helps that the syntax is quite
close to Python's own syntax for dictionaries.

Here's a quick example:

```python
>>> import json
>>> json.dumps(country_currencies)
'{"India": "Rupee", "Russia": "Ruble", "USA": "Dollar", "Japan": "Yen"}'
>>> json.loads(json.dumps(country_currencies)) == country_currencies
True
```

In short, these four functions from `json` module are enough to know the basic usage.

Method           | Description
---------------- | -----------
`.dump(obj, fp)` | Turn `obj` into JSON and write it to the `fp` file-like object.
`.dumps(obj)`    | Turn `obj` into JSON and return the resulting string.
`.load(fp)`      | Read valid JSON from `fp` file-like object and return the resulting object.
`.loads(data)`   | Parse `data` as a valid JSON string and return the resulting object.

As convenient as this is, it is important to know the changes to data types that will result because
of this. JSON only supports numbers, strings and booleans as primary data types and arrays & maps as
analogues to `list`s and `dict`s. As a result of this, if there are tuples somewhere in the
dictionary, then they will be turned into lists when the `dict` is serialized and deserialized with
JSON. A similar situation occurs for dates and any other data type not directly supported by the
JSON spec.

## Pickling

Unlike the above, pickling (using the [`pickle`][pickle-mod] module) serializes objects into binary
data and can handle a much wider range of data types. For this reason, pickled data can only be
loaded by Python, not other languages (well, not yet at least).

The `pickle` module has similar `dump`, `dumps`, `load` and `loads` methods just like for the above
discussed `json` module.

# The Item Syntax

The syntax used to get an item from a dictionary, given it's index, is `data[key]`. This is mostly
equivalent to calling the `__getitem__` method, like the following:

```python
data.__getitem__(key)
```

But obviously, we'd prefer the square bracket syntax. But understanding that underneath the syntax,
it's just a method call, lets us implement the `__getitem__` method in our own classes and get the
item syntax on our objects.

Here's a simple example:

```python
>>> class Store:
...     def __getitem__(self, name):
...             return name.upper()
...
>>> store = Store()
>>> store['Hello there!']
'HELLO THERE!'
```

Similar to this is the `__setitem__` which is used to set the value using the item syntax.

```python
# The following two are equivalent.
data[key] = value
data.__setitem__(key, value)
```

Note that this should be used responsibly. This feature gets into borderline operator overloading
category. In almost all cases (including the above example), using a normal named method on your
classes should be a better option than overriding the item syntax. Since a normal method would have
a name which makes the intent clearer.

# Flavors

Python's standard library comes with a few flavors of dictionaries that provide some nice additional
functionality. These data structures are all available in the [`collections`][collections] module.

The following are subclasses of `dict` and have all the features of Python's dictionaries.

## The `OrderedDict`

The [`collections.OrderedDict`][OrderedDict] is a dictionary that remembers the order in which keys
are *inserted*. The order remembered is the *insertion* order. So, if we add a new key to the dict,
it will be at the end of the key sequence. But if we change the value of an existing key, it's
position in the ordering is unchanged.

Create a new `OrderedDict`:

```python
>>> from collections import OrderedDict
>>> planet_satellites = OrderedDict(
...     Mercury=0,
...     Venus=0,
...     Earth=1,
...     Mars=2,
...     Jupiter=69,
...     Saturn=62,
...     Uranus=27,
...     Neptune=14,
... )
>>> from pprint import pprint
>>> pprint(planet_satellites)
OrderedDict([('Mercury', 0),
             ('Venus', 0),
             ('Earth', 1),
             ('Mars', 2),
             ('Jupiter', 69),
             ('Saturn', 62),
             ('Uranus', 27),
             ('Neptune', 14)])
```

Note that we use the [`pprint`][pprint] function to show the `OrderedDict` objects in a convenient
way.

They are just dictionaries under the hood.

```python
>>> isinstance(planet_satellites, dict)
True
>>> planet_satellites['Mars']
2
```

These objects support being reversed as well:

```python
>>> rev_planets = OrderedDict(reversed(planet_satellites.items()))
>>> pprint(rev_planets)
OrderedDict([('Neptune', 14),
             ('Uranus', 27),
             ('Saturn', 62),
             ('Jupiter', 69),
             ('Mars', 2),
             ('Earth', 1),
             ('Venus', 0),
             ('Mercury', 0)])
```

The results of `.keys` and `.values` methods also retain the ordering. Refer to the official
documentation linked above for full details.

## The `defaultdict`

{{% aside %}}
The name `defaultdict` is unfortunate as it doesn't adhere to any naming conventions. I'd love to
see it renamed to `default_dict` or even `DefaultDict`, but it's probably easier to just live with
it.
{{% /aside %}}

A `defaultdict` can understand how to initialize new keys. Consider the following code. Here, we
have a piece of text and we want a dictionary mapping each letter in the text to it's count of
occurrences.

```python
text = 'lorem ipsum dolor sit amet'
counts = {}
for letter in text:
    if letter not in counts:
        counts[letter] = 0
    counts[letter] += 1
print(counts)
```

{{% aside %}}
Of course, there's better ways to do this, but for the sake of example, let's bear with this
implementation.
{{% /aside %}}

Notice how we check if the letter is not already present in the dict and if so, we initialize it to
zero. A `defaultdict` can learn this method of initialization. It takes a function as its first
argument which returns the value of a new key when accessed. So, we can replace the above code to
use `defaultdict` like:

```python
from collections import defaultdict
text = 'lorem ipsum dolor sit amet'
counts = defaultdict(int)
for letter in text:
    counts[letter] += 1
print(counts)
```

When we try to get the value of a letter from `counts`, and that letter doesn't already exist in
`counts`, `defaultdict` will call `int`, with no arguments, and puts the return value into
`counts[letter]`. Precisely what we were doing in our previous example. So, what does `int` return
when called with no arguments? You guessed it, zero!

```python
>>> int()
0
>>> float()
0.0
>>> str()
''
>>> bool()
False
>>> list()
[]
>>> dict()
{}
>>> set()
set()
```

As illustrated above, calling the data type builtins with no arguments return the falsy value of
that data type. We can use this fact and pass these builtins to `defaultdict` constructor depending
on the need. If we wanted a different initial value, say `42`, we could use a lambda function like
`lambda: 42` instead.

## The `ChainMap`

The `ChainMap` is an abstraction over a chain of dictionaries in order of precedence. Essentially,
it holds a list of dictionaries and when a key is indexed, each of these dictionaries are searched
for this key and the value of the first match is returned.

This is better illustrated with an example. Let's create a `ChainMap` with dummy data:

```python
>>> from collections import ChainMap
>>> data = ChainMap({'a': 1, 'b': 2, 'c': 3}, {'c': 30, 'd': 40, 'e': 50})
>>> data
ChainMap({'a': 1, 'b': 2, 'c': 3}, {'c': 30, 'd': 40, 'e': 50})
>>> data.maps  # A list of maps in the chain.
[{'a': 1, 'b': 2, 'c': 3}, {'c': 30, 'd': 40, 'e': 50}]
```

Let's try indexing:

```python
>>> data['a']
1
>>> data['e']
50
>>> data['c']
3
```

Here, the `'a'` is indexed from the first dictionary, `'e'` is indexed from the second dictionary
and `'c'` is indexed from the first dictionary.

As mentioned in the documentation, writes, updates and deletes, however, operate on the first
dictionary alone.

```python
>>> data['a'] = 91
>>> data
ChainMap({'a': 91, 'b': 2, 'c': 3}, {'c': 30, 'd': 40, 'e': 50})
>>> data['e'] = 951
>>> data
ChainMap({'a': 91, 'b': 2, 'c': 3, 'e': 951}, {'c': 30, 'd': 40, 'e': 50})
>>> data['c'] = 93
>>> data
ChainMap({'a': 91, 'b': 2, 'c': 93, 'e': 951}, {'c': 30, 'd': 40, 'e': 50})
```

Of course, if we explicitly want to modify the last dictionary, it can be indexed directly:

```python
>>> data.maps[-1]['c'] = 999
>>> data
ChainMap({'a': 91, 'b': 2, 'c': 93, 'e': 951}, {'c': 999, 'd': 40, 'e': 50})
```

The `ChainMap` is useful to hold tiers of configuration parameters for an application, in a form
similar to the following:

```python
ChainMap(user_settings, default_settings)
```

We can have multiple tiers depending the situation. The user can modify the dictionary as they fit
and all writes and updates will be made only on the first dictionary, `user_settings`. Whereas, when
one tries to get the value of a configuration parameter, it automatically falls back to
`default_settings` if it isn't present in `user_settings`.

## The `Counter`

`Counter` dictionaries can be used to keep counts of any (hashable) objects. The keys are these
hashable objects and the values are their counts. The [official docs][Counter] on this gives some
clever examples and uses so I recommend you go read this up there, instead of redoing it here.

## Custom Flavor

Although rarely needed in practice, we can create our own flavors of dictionary types. One way to
achieve this would be to extend the `dict` type directly, but usually the easier way to deal with
this is to use the [`UserDict`][UserDict] class.

Here's an example dictionary type that works with string keys and is case-insensitive. A good use
for something like this is for HTTP headers. (The [requests][] library does [something
similar][requests-structures].)

```python
from collections import UserDict


class CaselessDict(UserDict):

    def __getitem__(self, name):
        return self.data[name.lower()]

    def __setitem__(self, name, value):
        self.data[name.lower()] = value
```

As seen above, the `UserDict` class provides a `.data` attribute that can be used as the underlying
store dictionary.

Let's try it out.

```python
>>> data = CaselessDict(accept='application/json')
>>> data['accept']
'application/json'
>>> data['Accept']
'application/json'
>>> data['ACCEPT']
'application/json'
```

# Disassembling

Now, let's disassemble a few common operations on dictionaries. I won't be going into the details of
how to interpret the disassembled instructions in this article. We use the [`dis`][dis] function
(from the aptly named `dis` module) for this.

Let's try this a very simple function.

```python
>>> dis.dis(lambda: {'a': 1})
  1           0 LOAD_CONST               1 ('a')
              2 LOAD_CONST               2 (1)
              4 BUILD_MAP                1
              6 RETURN_VALUE
```

Here, we see the [`BUILD_MAP`][BUILD_MAP] opcode that takes a count which is the length of the
dictionary to build. From the official docs,

> Pushes a new dictionary object onto the stack. Pops `2 * count` items so that the dictionary holds
> *count* entries: `{..., TOS3: TOS2, TOS1: TOS}`.

Now let's do this with two elements in the dict.

```python
>>> dis.dis(lambda: {'a': 1, 'b': 2})
  1           0 LOAD_CONST               1 (1)
              2 LOAD_CONST               2 (2)
              4 LOAD_CONST               3 (('a', 'b'))
              6 BUILD_CONST_KEY_MAP      2
              8 RETURN_VALUE
```

Here, we see a different opcode, [`BUILD_CONST_KEY_MAP`][BUILD_CONST_KEY_MAP] which also takes the
length of the dict as an argument. This is also explained best from the docs,

> The version of `BUILD_MAP` specialized for constant keys. *count* values are consumed from the
> stack. The top element on the stack contains a tuple of keys.

# Conclusion

Dictionaries in Python (or any other language for that matter) are a very powerful multi-purpose
data structure and are extremely handy and easy to use in Python. I hoped to put the things I
learned about them in this article. If you see any inaccuracies or if there's something that makes
for a good addition to this article, let me know in the comments below.

Thank you for reading. Please let me know what you think. If you have any topics you'd like me to
cover in a future article, put in a comment.

# References

The official documentation, mostly. Wikipedia for data used in examples.


[Dictionary]: https://docs.python.org/3.6/tutorial/datastructures.html#dictionaries
[hash]: https://docs.python.org/3/reference/datamodel.html#object.__hash__
[views]: https://docs.python.org/3.6/library/stdtypes.html#dictionary-view-objects
[.keys]: https://docs.python.org/3.6/library/stdtypes.html#dict.keys
[.values]: https://docs.python.org/3.6/library/stdtypes.html#dict.values
[.items]: https://docs.python.org/3.6/library/stdtypes.html#dict.items
[set-abc]: https://docs.python.org/3.6/library/collections.abc.html#collections.abc.Set
[typing.Dict]: https://docs.python.org/3/library/typing.html#typing.Dict
[mypy]: http://www.mypy-lang.org/
[PEP 274]: https://www.python.org/dev/peps/pep-0274/
[json-mod]: https://docs.python.org/3/library/json.html
[json.dump]: https://docs.python.org/3/library/json.html#json.dump
[json.load]: https://docs.python.org/3/library/json.html#json.load
[json]: http://json.org/
[pickle-mod]: https://docs.python.org/3/library/pickle.html
[collections]: https://docs.python.org/3/library/collections.html
[OrderedDict]: https://docs.python.org/3/library/collections.html#collections.OrderedDict
[pprint]: https://docs.python.org/3/library/pprint.html#pprint.pprint
[dis]: https://docs.python.org/3/library/dis.html#dis.dis
[BUILD_MAP]: https://docs.python.org/3/library/dis.html#opcode-BUILD_MAP
[BUILD_CONST_KEY_MAP]: https://docs.python.org/3/library/dis.html#opcode-BUILD_CONST_KEY_MAP
[Counter]: https://docs.python.org/3/library/collections.html#collections.Counter
[UserDict]: https://docs.python.org/3/library/collections.html#collections.UserDict
[requests]: http://docs.python-requests.org/en/master/
[requests-structures]: https://github.com/requests/requests/blob/master/requests/structures.py

