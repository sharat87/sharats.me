---
title: The Python `print` function
tags: python, print-function, tutorial
---

The [`print`][print] function is most likely the first function we encounter when learning Python.
That encounter usually looks like `print("Hello world!")`. After that, we go on to learning more
stuff about it like being able to pass any number of arguments or of any type etc. I'm writing this
article to give an idea how deep this rabbit hole goes. Turns out, the `print` function is *very*
powerful. So let's get a coffee, put on a dusty pair of sunglasses and bask in its power!

[TOC]

## The Basics

The basic premise of the `print` function is quite, well, basic. It prints out the given arguments
to the standard output.

```python
print("Hello world!")
```

This prints:

    Hello world!

Calling it with multiple arguments:

```python
print("hello", "world")
```

This prints:

    hello world

Notice that the two strings, `"hello"` and `"world"` have a space character printed between them.
The `print` function is helpful like that. By default, it places a space between every pair of
consecutive arguments to be printed.

It doesn't have to be strings either:

```python
print(42, "is the answer")
```

This prints:

    42 is the answer

Let's look at each of these features in detail and see how they work.

## Handling of Multiple Arguments

The `print` function accepts arbitrary number of arguments to be printed. These arguments can't be
keyword-arguments, because that doesn't make much sense. That's not to say the `print` function
doesn't accept any keyword arguments, it does. In fact, the space character that shows up between
the arguments to be printed, can be changed by providing the `sep=` keyword argument.

Let's look at the following examples:

```pycon
>>> print("the", "world", "is", "a", "cruel", "place")
the world is a cruel place

>>> print("the", "world", "is", "a", "cruel", "place", sep="-")
the-world-is-a-cruel-place

>>> print("the", "world", "is", "a", "cruel", "place", sep="")
theworldisacruelplace
```

In the first example, we don't explicitly give any value to the `sep=` keyword argument. So it takes
it's default value of the space character `" "`. In the second example, we set it to the dash
character `"-"` and we can see in the output that the strings are printed joined by dashes.

In the third example, we set the `sep=` to an empty string so the output is all the words printed
consecutively making it a cruel experience to read the text.

The `sep=` argument can be any string, it doesn't have to be a single character and it can contain
newlines and any other shenanigans too.

```python
print("the", "birds", "in", "the", "sky", sep="\n  hammertime\n")
```

This prints the following mind bogglingly useful output:

    the
      hammertime
    birds
      hammertime
    in
      hammertime
    the
      hammertime
    sky

Yeah that's a useful trick, but please, consider people's sanity when you do such !@#\$.

## Handling of non-string types

We know that the `print` function can handle printing objects of any type, not just strings. But how
does that work? The simple answer to this is that `print` will call `str` on non-string objects, and
print the result of that call.

Let's experiment with this. Consider the following class definition, which has just one method, the
`__str__`. If you are unaware of this method, this is what's called when `str` is applied on an
instance of this class. I won't go into details of that as that's not the topic of this article.

```python
class Tantrum:
    def __str__(self):
        return "awesome __str__ of object %r" % id(self)


print(Tantrum())
```

The output of running this would be something like (the number in the end would obviously be
different if you run this script):

    awesome __str__ of object 4508612624

So, what happens if our class doesn't define an implementation for the `__str__` method? Let's try
that out:

```python
class LazySloth:
    pass


print(LazySloth())
```

This prints the following output (again, the number in the end would obviously be different for
you):

    <__main__.LazySloth object at 0x105f327d0>

Turns out that when there's no implementation for `__str__`, calling `str` on the instance will
still produce some information regarding the instance, which is what we got above.

A neat thing here is that this output is actually what calling `repr` on the instance would produce.
So, it looks like `str` is falling back to returning the output of `repr`, when there's no
implementation for `__str__` provided. Let's confirm this by defining a `__repr__` method:

```python
class RatInFormals:
    def __repr__(self):
        return "a sad overridden __repr__ for instance %r" % id(self)


print(RatInFormals())
```

This prints the following output (again, the number will be different for you):

    a sad overridden __repr__ for instance 4313389264

Now we get the output of the overridden `__repr__`.

So here's how it works. The `print` function calls `str` on any non-string objects, which returns
the result of the `__str__` method, if available, or the result of calling `repr` on the instance,
which in turn returns the result of the `__repr__` method, which results in a generic output unless
overridden (like in the last example above).

This should be case in favor towards spending a few seconds thinking about and writing useful
`__str__` methods for your custom types. Someone walking along working with your code later on,
might just print an instance of your class to see what's in it, and the generic output with the
instance's `id` is unlikely to be very helpful.

## Write to files

Another keyword argument accepted by `print` is `file=`. This can be set to a `file` object, in
which case the *printing* will be done to that file object instead of standard output.

Let's try writing text to a file using the `print` function like this:

```python
with open("outputs.txt", "w") as f:
    print("Stuff that doesn't show up in standard output", file=f)
```

Running this script obviously doesn't print anything to the standard output. Instead, a file
"outputs.txt" is created which contains the following text:

    Stuff that doesn't show up in standard output

Note that since we are opening the file with mode as `"w"`, so if a file named "outputs.txt" already
exists in the current folder, it **will be overwritten**.

### Using `sys.stderr`

The [`sys.stderr`][sys.stderr] object in the `sys` module is a file-like object that represents the
standard error. Writing to this file-like object directs it to the standard error stream. This is
similar to the [`sys.stdout`][sys.stdout] object which represents the standard output stream, in a
similar fashion.

The `file=` keyword argument can be set to `sys.stderr` which will print to the standard error
stream.

```python
import sys

print("stuff going to standard error", file=sys.stderr)
```

You might not notice any difference from setting the `file=` argument in the above script, but if
you are running a terminal emulator / shell that shows standard error in red color, then you'll be
able to see a difference.

### Modifying `sys.stdout`

If we don't set a value explicitly to the `file=` argument, the output will be sent to the standard
output. There's a small note to that point to be observed. In reality, the output will be sent to
the `sys.stdout` file object. Usually, these two are the same. But, of course, we can set
`sys.stdout` to something else.

Consider the following script which changes the value of `sys.stdout`, prints something, and then
restores the value of `sys.stdout` to its original value.

```python {"linenos": true}
import sys

original_stdout = sys.stdout
with open("out.txt", "w") as f:
    sys.stdout = f
    print("trololololol")

sys.stdout = original_stdout
print("restored")
```

If we run this script, we'll only see `restored` in the output, but the file `out.txt` will be
created with the output from line 6.

A minor point to note here is that it's probably incorrect to say *"the default value of the `file`
argument is `sys.stdout`"*. Since if that were the case, changing the value of `sys.stdout` should
not affect the `print` function. Instead, I believe its default value is `None` and in that case,
`print` uses the current value of `sys.stdout`.

We can verify this by explicitly passing in `None` to the `file=` argument:

```python
import sys

original_stdout = sys.stdout
with open("out.txt", "w") as f:
    sys.stdout = f
    print("trololololol", file=None)


sys.stdout = original_stdout
print("restored", file=None)
```

The above script produces the exact same output as when we didn't provide the `file=` argument
explicitly.

### Collecting with `io.StringIO`

The [`io.StringIO`][io.StringIO] can be used to create a file object that collects all that is
written to it, and then get it all out as a string. This is useful when calling a function that
prints information using the `print` function, but instead, we want that output as a string for
further processing. We can replace `sys.stdout` with a `io.StringIO` instance before calling that
function, and then restore it after. Here's how this might look like:

```python {"linenos": true}
import io, sys

def print_product(a, b):
    print(a * b)


original_stdout = sys.stdout
string_io = io.StringIO()

sys.stdout = string_io
print_product(4, 5)
sys.stdout = original_stdout

result = string_io.getvalue()
print("Result is", result)
```

In this script, the `print_product` function prints the result of the multiplication, instead of
returning it. So to get the result out of it, we replace `sys.stdout` with a `io.StringIO` instance
and after calling the `print_product` function, we get the printed result using the `.getvalue()`
method.

However, note that a similar operation with binary data using `io.BytesIO` is not possible, since
the `print` function converts all its argument to text before writing to the file.

## The `end=` keyword argument

This is like one of those things that we notice only when it's taken away. The `print` function
appends a newline at the end of the last argument to be printed. Check out the following example:

```python
print("hello on day 1")
print("yeah right on day 2")
print("oh to hell with you on day 3")
```

The output of this script is the following:

    hello on day 1
    yeah right on day 2
    oh to hell with you on day 3

The output from the three `print` calls shows up in three separate lines, nice and neat. But we
never gave a `"\n"` in our calls to `print`. It comes from the default value of the `end=` argument
of the `print` function. If we set the `end=` argument to something else, it will replace the
newline in the end of the output from a `print` call.

Check out the following script for example:

```python
print("Doing awesome stuff... ", end="")
# do awesome stuff here
print("done")
```

This script prints the following output:

    Doing awesome stuff... done

The output of the two `print` calls shows up on the same line, since we suppressed the newline that
would've been printed from the first call to `print`, by setting the `end=` argument to an empty
string. The second call to `print` will continue this sentence and finish the line by adding a
newline at the end.

## A Note about Python 2

Python 2 had a `print` **statement**, which worked similar to the `print` **function** in Python 3,
but is not as feature-rich. Additionally, being a statement, it couldn't be used in all the places,
for example, within in a lambda expression.

However, Python 2.6 introduced a [future import][] that brought the `print` function to Python 2.
Adding a `from __future__ import print_function` line at the start of a Python 2 file would disable
the `print` statement in that file and turn `print` into a function. This can be very useful for
when migrating to Python 3.

## A Sad Imitation

Here's a sad little imitation of the `print` function that should behave similar to the builtin in
most of the features that have been discussed in this article:

```python
import sys

def sad_print(*args, sep=" ", end="\n", file=None):
    (sys.stdout if file is None else file).write(sep.join(map(str, args)) + end)


sad_print("the answer is", 42)
```

In this `sad_print` function, what we are essentially doing is:

1. Pick `sys.stdout` if `file` is `None`.
1. Call `str` on all of the provided arguments.
1. Join the results of the calls to `str` using the value of `sep`.
1. Concatenate the value of `end` to the result of above step.
1. Call write on result of point-1, with the result of the above step.

I'm sure the `print` builtin does quite a bit more than just this one-liner, but doing this can give
us some perspective of how all the different pieces fit in together.

## The `pprint` Function

Python's standard library has a [`pprint`][pprint] module, with a `pprint` function that takes one
argument, and prints it *prettily*.

For example, consider the following script:

```python
from pprint import pprint

numbers = [1, 2, 3, 4, 5, 6]

print(numbers)
pprint(numbers)

planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

print(planets)
pprint(planets)
```

We are calling `print` and `pprint` on the same list of strings. Let's look at the output:

    [1, 2, 3, 4, 5, 6]
    [1, 2, 3, 4, 5, 6]
    ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
    ['Mercury',
     'Venus',
     'Earth',
     'Mars',
     'Jupiter',
     'Saturn',
     'Uranus',
     'Neptune',
     'Pluto']

As we can see, the output from `pprint` is prettified, but only if necessary. In the first case,
where we were printing just six numbers, the output was fine as a single line so `pprint` did not
cut it up into several lines. But in the second case, the line ends up too long and it may not be
comfortable on small terminal screens. So, it cuts it up.

The `pprint` module can be useful to prettily print (or formatting) lists and dictionaries. Check
out its official documentation for more information.

## Conclusion

We may not use all these features of the `print` functions all the time, but I think it's useful to
know that `print` is not just a function that prints the given string. It's quite a bit more than
that; and when we need it, it's there without having to import anything. Thank you for reading!


[print]: https://docs.python.org/3/library/functions.html#print
[sys.stderr]: https://docs.python.org/3/library/sys.html#sys.stderr
[sys.stdout]: https://docs.python.org/3/library/sys.html#sys.stdout
[io.StringIO]: https://docs.python.org/3/library/io.html#io.StringIO
[future import]: https://docs.python.org/2/library/__future__.html
[pprint]: https://docs.python.org/3/library/pprint.html
