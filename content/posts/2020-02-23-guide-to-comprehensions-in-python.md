---
title: Guide to Comprehensions in Python
tags: python, programming, tutorial
description: This is a thorough guide to the various forms of comprehension expressions in the Python programming language. Contains several examples of list, set, and dictionary comprehensions.
reddit_url: r/Python/comments/faaj8q
---

Comprehensions are a syntax construct used for applying some form of transformations and filtering
over streams of data. The problems comprehensions solve can be done without them, using plain old
`for`-loops, but where possible, comprehensions can improve readability and show the intent very
well.

This article assumes some familiarity with Python (and comprehensions as well). I will go over the
basics of comprehensions quickly and jump into the meat of the article. Most of this article applies
for Python 3, unless otherwise specified.

If you're here for the live converter or comprehension &hArr; `for`-loop code, [it's further down in
the page](#live-code-converter).
{: .note }

[TOC]

## Basic Syntax

Let's go over the basic syntax for starters. It can be divided into three parts. The result
expression, the looping construct(s) and the filter expression. Of these, the filter expression is
optional, but the other two are required. Let's look at a simple example to get an idea:

```pycon
>>> [n ** 2 for n in range(4)]
[0, 1, 4, 9]
```

This is a *list comprehension* with no filtering (*i.e.,* no `if` clause). Here, the `n ** 2` part
is the result expression and the `for n in range(4)` is the looping construct. This comprehension
expression is the same as the following piece of code, written without comprehensions:

```pycon
>>> squares = []
>>> for n in range(4):
...     squares.append(n ** 2)
...
>>> squares
[0, 1, 4, 9]
```

Comprehensions also support conditions on the looping variables. For instance, in the example above,
if we only wanted squares of even numbers, we could do:

```pycon
>>> [n ** 2 for n in range(4) if n % 2 == 0]
[0, 4]
```

In this case, the result expression is not evaluated when the `n % 2 == 0` turns out to be `False`.

The keen Pythonista might note that this can be accomplished more simply by using the `step`
argument of the `range` builtin, but please excuse me for lacking in creativity for the examples!
{: .note }

## Different Collectors

In addition to `list` comprehensions, Python supports `set` and `dict` comprehensions as well. Where
`list` comprehensions collect the result values in a `list`, the latter two collect them in `set`s
and `dict`s respectively.

The syntax is almost exactly same as that of the list comprehensions. The only difference is that we
use braces for set and dict comprehensions, where we use square brackets for list comprehensions.
The looping and filtering constructs behave the same way. The result expression behaves the same way
for set comprehensions, but for dict comprehensions, we have to provide two expressions, the key and
the value, separate by a colon. Let's look at some examples:

```pycon
>>> [color.lower() for color in ['Blue', 'Red', 'blue', 'yellow']]
['blue', 'red', 'blue', 'yellow']

>>> {color.lower() for color in ['Blue', 'Red', 'blue', 'yellow']}
{'blue', 'red', 'yellow'}
```

The first expression in the above REPL session is a list comprehension and the second is a set
comprehension. Notice that the only difference in the first and third lines is the surrounding
bracket type.

```pycon
>>> {color.lower(): len(color) for color in ['Blue', 'Red', 'blue', 'yellow']}
{'blue': 4, 'red': 3, 'yellow': 6}
```

This is a dictionary comprehension. Notice here, the result expression is a *key-value pair of
expressions*, as opposed to a single expression for list and set comprehensions.

Note that these two forms of comprehensions have been introduced in Python 2.7 & 3. In the previous
versions, we could replicate this by calling the `set` and `dict` builtins over list comprehensions.
Here's an example:

```pycon
>>> set([color.lower() for color in ['Blue', 'Red', 'blue', 'yellow']])
{'blue', 'red', 'yellow'}

>>> dict([(color.lower(), len(color)) for color in ['Blue', 'Red', 'blue', 'yellow']])
{'blue': 4, 'red': 3, 'yellow': 6}
```

For dictionaries, we create a list of 2-tuples (key-value pairs) and pass that to `dict`.

## Multiple Looping Constructs

In the previous examples, we've only used one looping construct. However, it is possible to use
more than one looping construct. This works very similar to a nested `for`-loop. Let's look at an
example:

```pycon
>>> [(i, j) for i in range(0, 3) for j in range(10, 13)]
[(0, 10), (0, 11), (0, 12), (1, 10), (1, 11), (1, 12), (2, 10), (2, 11), (2, 12)]
```

This output is easy to visualize if you see the two `for`-loops nested. The following is a
reproduction of the above, without comprehensions:

```pycon
>>> result = []
>>> for i in range(0, 3):
...     for j in range(10, 13):
...         result.append((i, j))
...
>>> result
[(0, 10), (0, 11), (0, 12), (1, 10), (1, 11), (1, 12), (2, 10), (2, 11), (2, 12)]
```

This can go further levels of nesting, although if you have comprehensions with more three levels of
nesting, you should probably rethink your data structures or the way you're working with them.

Multiple looping constructs work just fine for set and dict comprehensions as well. Here's some
examples with set comprehensions and using a condition expression as well:

```pycon
>>> {(i, j) for i in range(0, 3) for j in range(10, 13)}
{(1, 12), (2, 11), (0, 12), (2, 10), (0, 11), (0, 10), (2, 12), (1, 10), (1, 11)}

>>> {(i, j) for i in range(0, 3) for j in range(10, 13) if j - i > 10}
{(0, 11), (1, 12), (0, 12)}
```

A subtle point here that's not easy to notice in the comprehensions is that the `range(10, 13)` call
in the above examples is called *three* times, whereas the `range(0, 3)` is called *once*. This
becomes obvious if you visualize this as the nested `for`-loop illustrated above. This is important
when using generators or iterators that work single-pass, like `map` objects, or file objects (for
which, we'll need `.seek`). Check out the following example to see what I mean:

```pycon
>>> range_for_i = map(str, range(0, 3))
>>> range_for_j = map(str, range(10, 13))

>>> [(i, j) for i in range_for_i for j in range_for_j]
[('0', '10'), ('0', '11'), ('0', '12')]
```

In this example, the `map` objects are destroyed once they have yielded all their results. That is
why the `range_for_j` only produced the three numbers only once, which were enough to pair with just
`'0'`, and there's no more to be paired with `'1'` and `'2'`.

You're not likely to encounter this in real-world code, but it's good to know lest we end up facing
it.

### Zipping instead of Cross Product

Using multiple `for` loops like above creates a sort-of cross-product. This is by nature of the
nested loop structure. But what if we're looking for a sort-of dot-product like result? Python
provides the `zip` builtin for this purpose. It is so specific to this problem, that using a
comprehension looks like unnecessary ceremony:

```pycon
>>> [(i, j) for i, j in zip(range(0, 3), range(10, 13))]
[(0, 10), (1, 11), (2, 12)]

>>> list(zip(range(0, 3), range(10, 13)))
[(0, 10), (1, 11), (2, 12)]
```

Of course, if we're doing some operation with `i` and `j` instead of just creating tuples, the
comprehension would still be very useful.

```pycon
>>> [i * j for i, j in zip(range(0, 3), range(10, 13))]
[0, 11, 24]
```

## Rewriting Comprehensions `map` & `filter` Builtins

Comprehensions can usually be a more-readable alternative to code written using `map` and/or
`filter` functions.

I've discussed the `map` builtin in more detail in [a previous article][map-article]. Not all
features of a comprehension can be translated with just the `map` function. In particular, there's
no way to apply a condition like we can in comprehensions, when using the `map` function alone. It
can be done if we also make use of the `filter` builtin. Here's an example of how such a
comprehension can be rewritten with `map` and `filter`.

```pycon
>>> [n ** 2 for n in range(10) if n % 2 == 0]
[0, 4, 16, 36, 64]

>>> list(map(lambda n: n ** 2, filter(lambda n: n % 2 == 0, range(10))))
[0, 4, 16, 36, 64]
```

Obviously, the comprehension reads much better, but I'd urge you to not just throw away the `map`
and `filter` builtins. They have their place and sometimes, code using them can read much better
than comprehensions. Check out my [article on `map` function][map-article] for such examples and
other rationales.

## Reducing with Assignment Expressions

I've actually stumbled on a version of this idea on Reddit. Unfortunately I don't have the source,
so, wherever you are, thank you!

The `functools` module from the standard library provides the [`reduce`][functools.reduce] callable
which can be used to systematically aggregate values in collections. I won't go into details of how
this can be used, but I will show how such an affect can be reproduced with comprehensions.

Let's look at an example of using the `functools.reduce`:

```pycon
>>> import functools
>>> functools.reduce(lambda acc, item: acc * item, range(1, 5), 1)
24
```

A simple implementation of the `reduce` function is provided at the official documentation and it's
a better explanation that I can provide here. Instead, we'll try and reproduce this with
comprehensions.

For this, we have to first familiarize ourselves with the [walrus operator][]. This is a new feature
in Python 3.8, that lets us do assignments in expressions. This means we'll now be able to do
assignment operations in places where only expressions (and not statements) are allowed, like the
result expression spot in comprehensions.

*By the power of the gray walrus*, we can reproduce `functools.reduce`:

```pycon
>>> acc = 1
>>> [acc := acc * item for item in range(1, 5)]
[1, 2, 6, 24]
>>> _[-1]
24
```

Although that works, and is quite nice, I'm not sure how readable that is. But I can attribute my
discomfort to the fact that this is uses a new language feature and like anything in life, needs
some getting used to. Also since it's new in version 3.8, it's probably best to stay away from it in
production code for a little while.

## Set Operations with Comprehensions

Comprehensions lend themselves quite well for set operations like intersection and difference.
They'll probably be less performant (and even less obvious to readers of such code), but
nonetheless, it's a nice example to play with:

```pycon
>>> rgb_colors = {"red", "green", "blue"}
>>> ryb_colors = {"red", "yellow", "blue"}

>>> intersection = {c for c in rgb_colors if c in ryb_colors}
>>> intersection
{'red', 'blue'}

>>> difference = {c for c in rgb_colors if c not in ryb_colors}
>>> difference
{'green'}
```

These are the same results we'd get if we used the standard set operators / methods:

```pycon
>>> rgb_colors & ryb_colors
{'red', 'blue'}

>>> rgb_colors - ryb_colors
{'green'}
```

Again, use the standard set functionalities for this, not the comprehension based methods I
illustrated above. If you do use the comprehension method of doing this in production, don't point
to me or this article as inspiration.

## Generator Expressions

When comprehensions are wrapped in square brackets or braces, the result is a fully realized
collection, like a list or a set. However, when not wrapped as such, or when wrapped with just
parentheses, the result is a generator expression, with none of result items realized. The result
items are realized as needed, like for example, if it's used in a `for`-loop.

Consider the following example session:

```pycon
>>> [n ** 2 for n in range(4)]
[0, 1, 4, 9]

>>> n ** 2 for n in range(4)
<generator object <genexpr> at 0x0000000005768DC8>
```

We can use this generator object in a `for`-loop or, perhaps more typically, in an aggregation
function, like `sum` or `max` etc.

```pycon
>>> squares = n ** 2 for n in range(4)
>>> sum(squares)
14
```

Of course since this is a generator expression, it can be iterated over *only once*. If you want to
iterate over it multiple times, just turn it into a list.

Generator expressions were introduced in [PEP-289](https://www.python.org/dev/peps/pep-0289/), which
contains a lot of examples. I recommend reviewing it for some cool use cases, which I won't
reproduce here.

One small note regarding passing generator expressions as an argument to functions is that, make it
a best practice to always wrap them with parentheses. The reason is, when using a generator
expression as an argument to a function, and when it is not the *only* argument to the function, we
may get an error that the generator expression is not parenthesized. Check out the following example
if that doesn't make sense:

In the following call to `sorted`, we pass in a generator expression as the sole argument, and we
get the expected result.

```pycon
>>> sorted(word.lower() for word in "We are from planet Earth, what's up?".split())
['are', 'earth,', 'from', 'planet', 'up?', 'we', "what's"]
```

Now to the same call, we add the `key` argument hoping to sort by the string lengths. Instead, we
get a `SyntaxError` because our generator expression is not parenthesized.

```pycon
>>> sorted(word.lower() for word in "We are from planet Earth, what's up?".split(), key=len)
  File "<stdin>", line 1
SyntaxError: Generator expression must be parenthesized
```

So, if we add parentheses to the generator, it works fine and we get the expected result.

```pycon
>>> sorted((word.lower() for word in "We are from planet Earth, what's up?".split()), key=len)
['we', 'are', 'up?', 'from', 'planet', 'earth,', "what's"]
```

## The `key` Argument for `sorted`

The `sorted` builtin provides the `key` argument that can be set to a function. This function is
applied to each item in the given list and the list items are sorted according to the sorting order
of the results of these function calls. This is a very convenient feature of `sorted`.

While this is probably a horrible thing to do, we could use comprehensions to recreate this effect
without using the `key` argument. The idea is that we first create a sequence of 2-tuples, where the
first items are the results of the `key` function and the second items are the original list items.
We then sort this sequence of tuples, extract the second items in each tuple and return that. Here's
an example implementation doing just that:

```python
def sad_sorted_with_key(items, key_fn):
    return [item for _, item in sorted((key_fn(item), item) for item in items)]


print(sad_sorted_with_key(
    (word.lower() for word in "We are from planet Earth, what's up?".split()),
    len,
))
```

This script would produce the following output:

    ['we', 'are', 'up?', 'from', 'earth,', 'planet', "what's"]

As usual, don't do this in production. This is just a sad experiment.

## No Side Effects Please

As best practice, please strive to have no side effects in your comprehension result expressions.
Check out the following example to see what I mean:

```pycon
>>> [print(n ** 2) for n in range(4)]
0
1
4
9
[None, None, None, None]
```

While this solves the purpose of printing the squares one per line, it also builds a list of
`None`s. It's also counter-intuitive when we treat comprehensions as applying a *transformation*
over each item in a collection. Calling `print` is not a transformation, it's a side effect.

For use cases like this, it's best to use a traditional `for`-loop:

```pycon
>>> for n in range(4):
...     print(n ** 2)
0
1
4
9
```

The intent here is clearer, which is to print each square, not to make a list of some results.

## Looking Inside

As another likely-pointless exercise, let's look at these comprehensions as Python bytecode, and
compare it with the same solution written using traditional `for`-loop.

First, let's define two functions that solve the same problem, but one uses comprehensions, and the
other doesn't.

```python linenos=true
def loop_squares():
    result = []
    for n in range(4):
        result.append(n ** 2)
    return result


def comp_squares():
    return [n ** 2 for n in range(4)]
```

Let's make sure they produce the same output:

```pycon
>>> loop_squares()
[0, 1, 4, 9]
>>> comp_squares()
[0, 1, 4, 9]
```

Now let's get the [`dis`][dis] module and disassemble both of these functions:

```pycon
>>> import dis
>>> dis.dis(loop_squares)
  2           0 BUILD_LIST               0
              2 STORE_FAST               0 (result)

  3           4 SETUP_LOOP              30 (to 36)
              6 LOAD_GLOBAL              0 (range)
              8 LOAD_CONST               1 (4)
             10 CALL_FUNCTION            1
             12 GET_ITER
        >>   14 FOR_ITER                18 (to 34)
             16 STORE_FAST               1 (n)

  4          18 LOAD_FAST                0 (result)
             20 LOAD_METHOD              1 (append)
             22 LOAD_FAST                1 (n)
             24 LOAD_CONST               2 (2)
             26 BINARY_POWER
             28 CALL_METHOD              1
             30 POP_TOP
             32 JUMP_ABSOLUTE           14
        >>   34 POP_BLOCK

  5     >>   36 LOAD_FAST                0 (result)
             38 RETURN_VALUE

>>> dis.dis(comp_squares)
  2           0 LOAD_CONST               1 (<code object <listcomp> at 0x7f3958a76c00, file "<stdin>", line 2>)
              2 LOAD_CONST               2 ('comp_squares.<locals>.<listcomp>')
              4 MAKE_FUNCTION            0
              6 LOAD_GLOBAL              0 (range)
              8 LOAD_CONST               3 (4)
             10 CALL_FUNCTION            1
             12 GET_ITER
             14 CALL_FUNCTION            1
             16 RETURN_VALUE

Disassembly of <code object <listcomp> at 0x7f3958a76c00, file "<stdin>", line 2>:
  2           0 BUILD_LIST               0
              2 LOAD_FAST                0 (.0)
        >>    4 FOR_ITER                12 (to 18)
              6 STORE_FAST               1 (n)
              8 LOAD_FAST                1 (n)
             10 LOAD_CONST               0 (2)
             12 BINARY_POWER
             14 LIST_APPEND              2
             16 JUMP_ABSOLUTE            4
        >>   18 RETURN_VALUE
```

I won't discuss each instruction in the above outputs, check out the official documentation of the
[`dis`][dis] module for that. But just skimming over the above, we can see one striking difference.
The comprehension function seems to have created a `code` object, which is doing the work of the
comprehension and passing (*returning*) the result to our `comp_squares` function. That sounds like
the `comp_squares` function is using an extra layer in the stack frame. We can confirm this by
changing the functions to the following:

```python linenos=true
import traceback

def loop_squares():
    traceback.print_stack()
    result = []
    for n in range(4):
        result.append(n ** 2)
    return result


def comp_squares():
    return [[traceback.print_stack() if n == 0 else None, n ** 2][1] for n in range(4)]
```

Let's see the stack they print and make sure they still produce the same result:

    >>> loop_squares()
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in loop_squares
    [0, 1, 4, 9]
    >>> comp_squares()
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in comp_squares
      File "<stdin>", line 2, in <listcomp>
    [0, 1, 4, 9]

The stack shows the file as `"<stdin>"` because I defined the functions within a REPL session. If
they were in an actual file, we'd obviously get the file name there.
{: .note }

As we suspected, the comprehension function adds another layer to the stack frame, the `<listcomp>`,
which is doing the work of the comprehension.

## Live Code Converter

Here's a little tool that converts your code written in the form of a list/set/dict comprehension,
into one that is written using traditional `for`-loops.

<div id=converterBox>
<textarea id=compCodeEl onKeydown="setTimeout(updateLoopCode)">[n ** 2 for n in range(9) if n % 2 == 0]</textarea>
<textarea id=loopCodeEl readonly></textarea>
<style>
#converterBox {
    display: flex;
    flex-wrap: wrap;
}
#converterBox textarea {
    flex-grow: 1;
    margin: 6px;
    height: 148px;
    font-size: inherit;
    font-variant-ligatures: none;
}
</style>
<script defer>
updateLoopCode();

function updateLoopCode() {
	document.getElementById("loopCodeEl").value = computeLoopCode(document.getElementById("compCodeEl").value);
}

function computeLoopCode(code) {
	code = code.trim();

	const closers = {'"': '"', "'": "'", "(": ")", "[": "]", "{": "}"};

	if (code[0] !== "[" && code[0] !== "{")
		return "";

	if (code[code.length - 1] !== closers[code[0]])
		return "";

	let type = code[0] == "[" ? "list" : "set";
	let i = 1;

	let expr = '';
	const stack = [], parts = [];

	for (; i < code.length - 1; ++i) {
		const ch = code[i];
		if (stack.length > 0 && ch === stack[stack.length - 1]) {
			expr += stack.pop();

		} else if (ch.match(/["'(\[{]/)) {
			expr += ch;
			stack.push(closers[ch]);

		} else if (stack.length > 0) {
			expr += ch;

		} else if (stack.length === 0 && ch === ":") {
			type = "dict";
			parts.push(expr);
			expr = '';

		} else {
			const match = code.substr(i).match(/^(for|if)\b/);
			if (match) {
				parts.push(expr);
				expr = ch;

			} else {
				expr += ch;

			}

		}

	}

	if (expr.length)
		parts.push(expr);

	for (const i in parts)
		parts[i] = parts[i].trim();

	const loopCodeLines = [];

	switch (type) {
		case "list":
			loopCodeLines.push("result = []")
			break;
		case "set":
			loopCodeLines.push("result = set()")
			break;
		case "dict":
			loopCodeLines.push("result = {}")
			break;
	}

	const resultPart = parts.shift(), resultValuePart = type === "dict" ? parts.shift() : null;

	let indentLevel = 0;
	for (const part of parts) {
		loopCodeLines.push(makeIndent(indentLevel) + part + ":");
		++indentLevel;
	}

	switch (type) {
		case "list":
			loopCodeLines.push(makeIndent(indentLevel) + "result.append(" + resultPart + ")");
			break;
		case "set":
			loopCodeLines.push(makeIndent(indentLevel) + "result.add(" + resultPart + ")");
			break;
		case "dict":
			loopCodeLines.push(makeIndent(indentLevel) + "result[" + resultPart + "] = " + resultValuePart);
			break;
	}

	return loopCodeLines.join('\n');
}

function makeIndent(level) {
	level *= 4;
	const spaces = [];
	while (level--)
		spaces.push(' ');
	return spaces.join('');
}
</script>
</div>

It's powered by an extremely light parser (doesn't even qualify to be called that), but it can help
illustrate the point. It can also be helpful for visualizing nested loops and comprehensions with
multiple `for` statements.

Here's some examples to try this with:

| Comprehension Code (click to put in converter)              |
| ----------------------------------------------------------- |
| `[n ** 2 for n in range(4)]`                                |
| `[n ** 2 for n in range(4) if n % 2 == 0]`                  |
| `{n ** 2 for n in range(4) if n % 2 == 0}`                  |
| `[r"abc def" for n in range(4)]`                            |
| `[(1, 2) for n in range(4)]`                                |
| `[n * m for n in range(4) for m in range(3) if n % 2 == 0]` |
| `{n * m for n in range(4) for m in range(3) if n % 2 == 0}` |
| `{n: n ** 2 for n in range(4) if n % 2 == 0}`               |

<style>
#examplesTable a { text-decoration: none }
</style>
<script defer>
{
const table = document.evaluate(
    "//th[starts-with(text(),'Comprehension Code')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)
    .singleNodeValue.closest('table');
table.id = 'examplesTable';
table.addEventListener('click', (event) => {
    if (event.target.tagName === 'A') {
        document.getElementById('compCodeEl').value = event.target.innerText;
        updateLoopCode();
    }
});
for (const codeEl of table.getElementsByTagName('code')) {
    codeEl.insertAdjacentHTML('afterBegin', '<a href="#"></a>');
    codeEl.firstElementChild.append(codeEl.firstElementChild.nextSibling);
}
}
</script>

<!-- TODO: Asynchronous comprehensions https://www.python.org/dev/peps/pep-0530/ -->

## Conclusion

Comprehensions are a powerful feature in Python that can create very readable code when used
correctly. However, like everything else, they have a place and time and it's not everywhere and
all-the-time. It's important to understand them well if you're doing more than the trivial list
comprehension.

Do check out the official documentation on [List Comprehensions][list-comp-official], which contains
a lot of *good* examples and ideas I didn't discuss here.

Additionally, at the expense of repeating the same thing, there's some experiments on this page that
are only intended for learning. Please do **not** use them in production code. Have pity on your
future self.


[map-article]: ../python-map-function/
[functools.reduce]: https://docs.python.org/3/library/functools.html#functools.reduce
[walrus operator]: https://docs.python.org/3/faq/design.html#why-can-t-i-use-an-assignment-in-an-expression
[dis]: https://docs.python.org/3/library/dis.html
[list-comp-official]: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
