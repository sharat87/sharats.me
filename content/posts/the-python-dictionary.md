---
title: The Python Dictionary
date: 2017-09-20T07:50:28+05:30
tags: ['python', 'data-structures']
draft: true
---

Dictionaries in Python are a key-value style data structures that are tightly integrated with the
language syntax and semantics. Understanding them well can help you utilize them better and
investigate subtle problems more effectively. This is my attempt to document this topic in more
depth.

This article is written for Python 3.6 installed via Anaconda on Xubuntu.

{{% toc %}}

# Introduction

Dictionaries (type `dict`) are a very powerful data structure, not just in Python. They are present
in almost every modern high level language, sometimes called maps. Python's syntax for dictionaries
inspired the syntax of the JSON serialization format.

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

indian_currency = country_currencies['India']

for country, currency in country_currencies:
    print(f"{country}'s currency is {currency}.")
```

{{% aside %}}
The above code uses [f-strings][] introduced in Python 3.6. In older versions of Python we have to
use the `.format` method or the modulo (`%`) operator.

[f-strings]: https://docs.python.org/3.6/reference/lexical_analysis.html#f-strings
{{% /aside %}}

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

# The Keys

The keys for the index of the dictionary.

The `.keys` method and what it returns.

# The Values

# Public Appearance

Dictionaries are very tightly integrated into Python's semantics. They pop up in a lot of places.
Here's a few ones.

## Function Keyword Arguments

When defining a function that takes arbitrary keyword arguments, they are passed to the function as
a dictionary.

```python
def construct(**counts):
    print(type(counts), len(counts))
```

## Globals

Using `globals`.

## Attributes / Properties

Using `vars`.

# Serialization

## JSON Objects

## XML Interfaces

## Pickling

# Ways of Constructing

# Typing

# Faking

# Additional Models

## The `OrderedDict`

### Example Applications

## The `defaultdict`

### Example Applications

## Extending `dict`

# Tuples

# Classes

# Conclusion

The `__dict__` attribute.
