---
title: Serializing python-requests' Session objects for fun and profit
tags: python, python-requests, python-pickle
hn_id: 9857170
---

## Prepare

If you haven't checked out @kennethreitz's excellent [python-requests][]
library yet, I suggest you go do that immediately. Go on, I'll wait for you.

Had your candy? That is one of the most beatiful piece of python code I've read.
And its an excellent library with a very humane API.

Recently, I have been using this library for a few of my company's internal
projects and at a point I needed to serialize and save `Session` objects for
later. That wasn't as straightforward as I first thought it'd be, so I am
sharing my experience here.

First off, let's make a simple http server which we are going to contact with
python-requests. The server should be able to handle cookie based sessions and
also have basic auth, as these things are handled by python-requests' Session
objects on the client side. I won't discuss the code for the server here, you
can get it from [the gist][server.py].

Once you have the server running, now for the client, lets do requests!

```python
import requests as req

URL_ROOT = 'http://localhost:5050'

def get_logged_in_session(name):
    session = req.session(auth=('user', 'pass'))

    login_response = session.post(URL_ROOT + '/login', data={'name': name})
    login_response.raise_for_status()

    return session

def get_whoami(session):
    response = session.get(URL_ROOT + '/whoami')
    response.raise_for_status()
    return response.text
```

I defined two functions here. The `get_logged_in_session` will create a new
session and login to the http server and return that session. Any subsequent
requests using this sesssion will be made as if you have logged in. That's what
will be tested with the `get_whoami` function, which will just return the
response from `/whoami`.

Lets test this out. Make sure the `server.py` is running and in another
terminal,

```python
$ python -i client.py
>>> s = get_logged_in_session('sharat')
>>> get_whoami(s)
u'You are sharat'
>>> get_whoami(req.session(auth=('user', 'pass')))
u'You are a guest'
```

Works perfectly. If we pass it the logged in session, it gives us the username
and if we pass it a new session, it gives us `a guest`.

Now, lets assume we have two functions, `serialize_session` and
`deserialize_session` which do exactly what their names say. We can test them
out by running a small test.py, as

```python
from client import get_logged_in_session, get_whoami
from serializer import deserialize_session, serialize_session

session = get_logged_in_session('sharat')
dsession = deserialize_session(serialize_session(session))

assert get_whoami(session) == get_whoami(dsession)
print 'Success'
```

and a dummy serializer.py

```python
def serialize_session(session):
    return session

def deserialize_session(session):
    return session
```

And with that, of course, the test will not fail

```
$ python test.py
Success
```

## Serializing

Now, to implement the functions in `serializer.py`. A simple one, would be to
use pickle. Lets try

```python
import pickle as pk

def serialize_session(session):
    return pk.dumps(session)

def deserialize_session(data):
    return pk.loads(data)
```

If you run `test.py` now, python is going to yell at you.

```
$ python test.py
Traceback (most recent call last):
    File "test.py", line 10, in <module>
    dsession = deserialize_session(serialize_session(session))
[ ... ]
    raise TypeError, "can't pickle %s objects" % base.__name__
TypeError: can't pickle lock objects
```

Oh well, it was worth a try I suppose.

**Update**: The Session class can be made to
[implement](#update-pickling-can-also-work) the pickle protocol if you want to
use pickle.

Next plan I had was to pick up attributes and data from a `Session` object, just
enough to recreate this object using the Session constructor, and serialize
those attributes as a JSON. After all, the Session's API is very easy to use,
how hard can picking attributes from it be? :)

So, I dug in the [sessions.py][] module of python-requests library. And here's
what the signature of the constructor for `Session` objects looks like

```python
def __init__(self,
    headers=None,
    cookies=None,
    auth=None,
    timeout=None,
    proxies=None,
    hooks=None,
    params=None,
    config=None,
    verify=True):
    # ...
```

So, if I pick up just these values, I should be able to recreate the session
object. Sweet.

```python
import json
import requests as req

def serialize_session(session):
    attrs = ['headers', 'cookies', 'auth', 'timeout', 'proxies', 'hooks',
        'params', 'config', 'verify']

    session_data = {}

    for attr in attrs:
        session_data[attr] = getattr(session, attr)

    return json.dumps(session_data)

def deserialize_session(data):
    return req.session(**json.loads(data))
```

And let's try this out

```
$ python test.py
Traceback (most recent call last):
    File "test.py", line 12, in <module>
    assert get_whoami(session) == get_whoami(dsession)
[ ... ]
[...]requests/models.py", line 447, in send
    r = self.auth(self)
TypeError: 'list' object is not callable
```

Okay, that error message is very weird. Why would anyone *call* a list object?

Go dig in the [models.py] module. See this

```python
[ ... ]
if isinstance(self.auth, tuple) and len(self.auth) == 2:
    # special-case basic HTTP auth
    self.auth = HTTPBasicAuth(*self.auth)

# Allow auth to make its changes.
r = self.auth(self)
[ ... ]
```

There. Its not a list that's being called. Not directly at least. The problem
here is that the `auth` we are passing to `session()` is not a tuple. Duh!
While I like it that `auth` is restricted to be a tuple, I wish there was a
better error message for when `auth` is a list instead of a tuple. I personally
wouldn't want it to accept a `list` for `auth` though.

So, what went wrong? `json` does not differentiate between a tuple and a list.
It only does lists. So, when serializing and deserializing, the `auth` tuple is
turned to a `list`. Lets turn it back

```python
def deserialize_session(data):
    session_data = json.loads(data)

    if 'auth' in session_data:
        session_data['auth'] = tuple(session_data['auth'])

    return req.session(**session_data)
```

And

```
$ python test.py
Traceback (most recent call last):
  File "test.py", line 12, in <module>
    assert get_whoami(session) == get_whoami(dsession)
  [ ... ]
  File "/usr/lib/python2.7/string.py", line 493, in translate
    return s.translate(table, deletions)
TypeError: translate() takes exactly one argument (2 given)
```

Wait. What? Now we have an error from stdlib? This just keeps getting better and
better. If this looks like something that can frustrate you, go get some coffee
:)

If you look at the complete stack trace, the second file from bottom,

```python
  File "[...]site-packages/requests/packages/oreos/monkeys.py", line 470, in set
    if "" != translate(key, idmap, LegalChars):
```

This thing seems to be calling the `translate` method incorrectly. With a bit of
debugging and yelling at my monitor, I found out the problem and for a moment,
lost my grip on reality.

`str.translate` takes 2 arguments, but `unicode.translate` takes only 1. I have
no idea why this is done this way but I sure as hell didn't enjoy it. The code
in `oreos/monkeys.py` assumes that the `key` is a `str`. However, what
`json.loads` gives you, is unicode stuff. So, we need to convert just the parts
in the deserialized dict we get from `json.loads` which are being used by the
`oreos/monkeys.py`, from `unicode` to `str`.

Reading a bit more code around the oreos library, it didn't take long to figure
out that those were the keys in the `cookies` dict. Lo

```python
def deserialize_session(data):
    session_data = json.loads(data)

    if 'auth' in session_data:
        session_data['auth'] = tuple(session_data['auth'])

    if 'cookies' in session_data:
        session_data['cookies'] = dict((key.encode(), val) for key, val in
                session_data['cookies'].items())

    return req.session(**session_data)
```

And so

```
$ python test.py
Success
```

**!**

All the code is on a [gist][].

## Update: Pickling can also work

As *Daslch* pointed out in his [comment][] on reddit, by implementing the pickle
protocol on the Session class, we can get pickling to work. From the
[documentation][], we need two methods, `__getstate__` and `__setstate__`.

Adding those methods as follows to `sessions.Session` class

```python
def __getstate__(self):
    attrs = ['headers', 'cookies', 'auth', 'timeout', 'proxies', 'hooks',
        'params', 'config', 'verify']
    return dict((attr, getattr(self, attr)) for attr in attrs)

def __setstate__(self, state):
    for name, value in state.items():
        setattr(self, name, value)

    self.poolmanager = PoolManager(
        num_pools=self.config.get('pool_connections'),
        maxsize=self.config.get('pool_maxsize')
    )
```

with this as the version of `serializer.py` that uses pickle, we do get a
`Success`.

The creation of new poolmanager in `__setstate__` is a piece of code copied from
`__init__` of the same class. This should probably be turned to a method to
avoid code repetition.

**Update 2**: Created an [issue][] about this.

**Update 3**: This has been merged and Session objects are pickleable as of
version 0.10.3. See [requests history][].

[comment]: http://www.reddit.com/r/Python/comments/pv1lf/serializing_pythonrequests_session_objects_for/c3sh5bb
[documentation]: http://docs.python.org/library/pickle.html#object.__getstate__
[gist]: https://gist.github.com/2660997
[issue]: https://github.com/kennethreitz/requests/issues/439
[models.py]: https://github.com/kennethreitz/requests/blob/develop/requests/models.py#L447
[python-requests]: http://docs.python-requests.org/en/latest/index.html
[requests history]: https://github.com/kennethreitz/requests/blob/develop/HISTORY.rst
[server.py]: https://gist.github.com/2660997#file_server.py
[sessions.py]: https://github.com/kennethreitz/requests/blob/develop/requests/sessions.py#L50
