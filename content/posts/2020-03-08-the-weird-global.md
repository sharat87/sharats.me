---
title: The Weird `global`
tags: python, rant
description: >
    Usage of the global keyword and how it can be unintuitive some times, with lots of examples and
    details.
---

Python's `global` keyword allows us to change the value of module-level variables inside functions.
Sounds so simple and useful, doesn't it? Well, yeah. I'm going to show you how it can be useful in
the simple sense and situations where it can drive people nuts.

## Simple Usage

Consider the following `top.py` script. We have a single module-level (aka `global`) variable here
and we change it's value in the function `done`.

```python linenos=true filename=top.py
are_we_done = False


def mark_done():
    global are_we_done
    are_we_done = True


print("Done?", are_we_done)
mark_done()
print("Done?", are_we_done)
```

Running this, we get the following output:

    Done? False
    Done? True

The reason we were able to change the value of the global variable `are_we_done` from inside the
`mark_done` function is because we declared it as such on line 5. If that declaration isn't there,
we'd just be defining a new *function level variable* called `are_we_done` inside the `mark_done`
function. Which is not what we wanted.

## Refer Directly

Note that declaring variables as `global` is needed only when we're *modifying the value of the
variable*. That means if we are only accessing the variable, we don't need to declare it as
`global`. This is how capitalized constant variables work in most Python scripts:

```python
CURRENT_PLANET = "Earth"


def get_moon_count():
    if CURRENT_PLANET == "Earth":
        return 1
    else:
        raise ValueError("No idea!")


print(get_moon_count())
```

This, of course, prints out `1`. Here, we are using the `CURRENT_PLANET` global variable inside the
function without declaring it as global. Accessing doesn't *require* explicitly declaring as
`global`.

### Modifying the Referred Object

A small note on the terms we've been using here. Accessing doesn't require `global` declaration, but
modifying does. Now look at the following code snippet:

```python
CALLS = []


def record_call(phone_number):
    CALLS.append(phone_number)


record_call("123-45-678")
record_call("987-65-432")
print(CALLS)
```

Here, since we are appending to the `CALLS` list, is that considered modifying the global variable?
The answer is *no*. We are merely *accessing* the `CALLS` variable's value, which happens to be a
`list`, on which we call the `.append` method. There's no modifying going on here so far. The
`.append` method, however, will change the *state* of the `list` object. But for the purposes of
using the `CALLS` variable here, we are only accessing it. So, we don't need to declare it as
`global`.

So what *does* modifying mean? Simply put, if you want to reassign a global variable, it's
considered as modifying.

## Assigning without Declaring

This behaviour of global variables causes some slightly unintuitive situations. For example,
consider the following piece of code:

```python linenos=true
is_server_up = False


def mark_server_up():
    print(is_server_up)


mark_server_up()
```

In this script, we are using the global variable `is_server_up` on line 5, without declaring it as
`global`, and it works fine. Now, we add another line to this function:

```python linenos=true
is_server_up = False


def mark_server_up():
    print(is_server_up)
    is_server_up = True


mark_server_up()
```

If we run this script, we get the following error:

    Traceback (most recent call last):
      File "/check.py", line 9, in <module>
        mark_server_up()
      File "/check.py", line 5, in mark_server_up
        print(is_server_up)
    UnboundLocalError: local variable 'is_server_up' referenced before assignment

Okay, we kind of expected an error because we are trying to modify a global variable without
declaring it. But note that the error comes from **line 5**, not on **line 6**, where we are
modifying the variable. The error message gives a hint on what's happening.

    local variable 'is_server_up' referenced before assignment

Since we didn't declare `is_server_up` as global, and since we are setting a value to
`is_server_up`, Python decided that we want a local variable in our function with the same name.
With that understanding, it looks like we are referencing the `is_server_up` *local variable* before
assigning a value to it. That's the error we see here.

## Conclusion

Global variables have their place, but, if it's not for constant-like values, I'd recommend against
using global variables at all. It might make sense for small one-off scripts, and when it does, keep
the above small details in mind.
