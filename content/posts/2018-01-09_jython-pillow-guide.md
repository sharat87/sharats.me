---
title: The Jython Pillow Guide
tags: [python, jython, java, polyglot]
description: >
    Expert tips on writing Python programs tailored to run on Jython, making the best use of
    Jython's features and Java interop.
---

This is a document with tips and usage details about Jython that I've come across. I intend to
document handy features of Python as well as some clever inter-op facilities provided by Jython.

I'm going to assume you're not a complete beginner to Java and Python languages. If you find
anything off or have a suggestion to add, please do write to me. Thanks!

## Logging and Printing

When using Apache's *log4j*, we can get an instance of a `Logger` using the API just as we would in
Java:

```python
>>> from org.apache.log4j import Logger
>>> log = Logger.getLogger('jython_script')
```

When getting a `Logger` instance for a module that is imported, a logger with a category specific to
that module can be obtained using the following code:

```python
log = Logger.getLogger(__name__)
```

The `__name__` name is a variable containing the current module's name as a string. *Note* that
`__name__` is set to the string `'__main__'` if the module is run as a script and not imported from
another script. This should be kept in mind when using the above code.

The standard printing functions of Java can be imported into Python and used directly in the
following way:

```python
>>> from java.lang import System
>>> System.out.println('Hola')
Hola
>>> System.err.println('Hello there')
Hello there
>>> System.out.print('Hola\n')
Hola
```

However, it's usually more convenient to use Python's `print` statement to output things to standard
output and error:

```python
print 'Hello world!'
```

Here's a table illustrating the `print` statement equivalents of the Java `print*` functions:

| Java                      | Python                      |
| ------------------------- | --------------------------- |
| `System.out.println("!")` | `print '!'`                 |
| `System.out.print("!")`   | `print '!',`                |
| `System.err.println("!")` | `print >> sys.stderr, '!'`  |
| `System.err.print("!")`   | `print >> sys.stderr, '!',` |

## Bean Properties

Jython can implicitly call the `.get*` and `.set*` methods that are widely used in Java classes to
get and set the values of instance attributes. Here's an illustration of how this inter-op works:

| Jython                        | Java equivalent                 |
| ----------------------------- | ------------------------------- |
| `obj.somePropertyValue`       | `obj.getSomePropertyValue()`    |
| `obj.somePropertyValue = 123` | `obj.setSomePropertyValue(123)` |

Of course, when such `.get*` and `.set*` methods are not available, this falls back gracefully to
trying get/set the property values directly, just as Java would treat those statements.

## Strings

Strings in Java (*i.e.,* objects of type `java.lang.String`) are converted to `unicode` objects when
passed in to Python world. Whereas `str` and `unicode` objects in Python are converted to
`java.lang.String` instances when passed in to Java world. This conversion is seamless and we
usually don't have to worry about it.

However, if needed, we can explicitly create an instance of `java.lang.String` from a `unicode`
object in Python:

```python
>>> from java.lang import String
>>> greeting = String('Hello')
>>> greeting
Hello
>>> type(greeting)
<type 'java.lang.String'>
```

String formatting using `%` operator in Python cannot be applied to Java `String` objects. They have
to converted to `str` or `unicode` first.

## Maps as Dictionaries

For the purposes of the following examples, let's work with the following
[`Map`](https://docs.oracle.com/javase/8/docs/api/java/util/Map.html):

```java
java.util.Map<String, Integer> data = new java.util.HashMap<>();
data.put("a", 1);
data.put("b", 2);
data.put("c", 3);
```

`Map`s support the *getitem* syntax very well so it is usually convenient to think of them as
python-style dictionaries. Here's an example:

```python
>>> print data['a']  # data.get("a")
1
>>> print data['b']  # data.get("b")
2
>>> data['d'] = 4  # data.put("d", 4)
>>> data['d']  # data.get("d")
4
>>> len(data)  # data.size()
4
>>> 'c' in data  # data.containsKey("c")
True
>>> del data['c']  # data.remove("c")
>>> 'c' in data  # data.containsKey("c")
False
>>> data
{a=1, b=2, d=4}
>>> len(data)  # data.size()
3
```

Although this resembles the usage of a traditional python dictionary, the methods you'd expect in a
dictionary are not all available. This is a `Map` object after all and it has the methods of the
`Map` class. However, it is easy to get see the parallels among some of the most used methods.

| `dict` method             | `Map` method                                                 |
| ------------------------- | ------------------------------------------------------------ |
| `.keys`                   | `.keySet`                                                    |
| `.values`                 | `.values`                                                    |
| `.clear`                  | `.clear`                                                     |
| `.items` (gives 2-tuples) | `.entrySet` (gives `Entry` objects with `.key` and `.value`) |
| `.update`                 | `.putAll` (accepts `dict` as well as a `Map`)                |

The `dict` builtin can be called on the `Map` object to get a python-style dictionary, if needed.
Additionally, just like a python dictionary, calling `list` (or `set`) on the `Map` object gives a
`list` (or `set`) of the *keys* in the `Map`.

Using `for` loops to iterate over `Map`s yields the keys in the `Map`, which is consistent with how
`for` loops work with python dictionaries.

```python
for key in data:
    print key, data[key]
```

Prints the following:

    a 1
    b 2
    d 4

In python, the `.items` method returns each entry as a `tuple` which lets us write the for loop like
the following:

```python
# !!! Only works if `data` is a python-style dictionary, not if it is a `Map`.
for key, value in data.items():
    print key, value
```

But unfortunately, since `Map` doesn't have the `.items` method, this is not possible. However, we
can use the `.entrySet` method to construct something *slightly* similar.

```python
for entry in data.entrySet():
    print entry.key, entry.value
```

To iterate over the values of a `Map`, since the method is called `.values` in both `dict` and
`Map`, the same piece of code would work with any object.

```python
for value in data.values():
    print value
```

Empty `Map` objects are treated as `False` in boolean contexts, just as with python's dictionaries.

## Collections

The two main collection types in Python are `list` and `set`. The equivalents in java are the
interfaces [`List`](https://docs.oracle.com/javase/8/docs/api/java/util/List.html) and
[`Set`](https://docs.oracle.com/javase/8/docs/api/java/util/Set.html). Let's prepare some data for
our examples.

```java
java.util.List<String> planets = new java.util.ArrayList<>();
planets.add("Mercury");
planets.add("Venus");
planets.add("Earth");

java.util.Set<String> colors = new java.util.HashSet<>();
colors.add("White");
colors.add("Black");
colors.add("Red");
colors.add("Green");
colors.add("Blue");
```

The *getitem* syntax can be used with `List`s seamlessly:

```python
>>> planets[0]
u'Mercury'
>>> planets[1]
u'Venus'
```

The slicing syntax, returns `List`s of the same type, not python-style `list`s.

```python
>>> planets[:2]
[Mercury, Venus]
>>> type(_)  # `_` is a variable set to the return value of last expression.
<type 'java.util.ArrayList'>
>>> planets[::-1]
[Earth, Venus, Mercury]
>>> type(_)
<type 'java.util.ArrayList'>
```

However, the *getitem* syntax is not supported for `Set`s as it doesn't make sense there since
`Set`s are unordered collections. But the operator support available for `set`s in python are
available with Java `Set` objects as well.

```python
>>> 'Red' in colors
True
>>> len(colors)
5
```

The `for` loop can be used on any
[`Collection`](https://docs.oracle.com/javase/8/docs/api/java/util/Collection.html) type objects to
iterate over the object's contents.

```python
>>> for x in planets:
...     print x
...
Mercury
Venus
Earth
>>> for x in enumerate(planets):
...     print x
...
(0, u'Mercury')
(1, u'Venus')
(2, u'Earth')
```

Here's equivalents for some of the methods available in Java's `Collection`s and Python's collection
types.

| Java                  | Jython                                                                  |
| --------------------- | ----------------------------------------------------------------------- |
| `Collection.add`      | `list.append` / `set.add`                                               |
| `Collection.addAll`   | `list.extend` / `set.update` (Prefer `list + list` or `set.union`)      |
| `Collection.contains` | `in list` or `in set`                                                   |
| `Collection.isEmpty`  | `bool(list)` or `bool(set)` (Can be used directly in a boolean context) |
| `Collection.size`     | `len(list)` or `len(set)`                                               |

Empty `Collection`s are treated as `False` in boolean contexts, just as with python's collections.

### Java Arrays

Just as Java's `List` is mirrored in Python with `list`, Java's arrays are mirrored using the array
structure available in Jython's [`array`](http://www.jython.org/docs/library/array.html) module.
That official documentation is quite exhaustive on this topic, so I suggest going over it to get an
idea of handling arrays in Jython.

## The Iteration Protocol

Java's [`Iterator`](https://docs.oracle.com/javase/8/docs/api/java/util/Iterator.html) style
iteration is supported by Jython's `for` statements. For example, consider the following Java
`Iterator` that's trying to emulate a small fraction of Python's `range` function:

```java
package ssk.experiments;
import java.util.Iterator;

public class RangeIterator implements Iterator<Integer> {
    private Integer current = 0, max;
    public RangeIterator(int max) { this.max = max; }
    @Override
    public boolean hasNext() { return current < max; }
    @Override
    public Integer next() { return current++; }
}
```

Since classes are instantiated without a `new` keyword in Python, combined with the fact that
Jython's `for` statement supports Java's `Iterator`s, we can use the above in the following way:

```python
from ssk.experiments import RangeIterator


for n in RangeIterator(5):
    print n
```

This gives the following output:

	0
	1
	2
	3
	4

Since Jython's `for` statement supports iterating over Java's
[`Enumeration`](https://docs.oracle.com/javase/8/docs/api/java/util/Enumeration.html) type, the
above same `for` loop would work with a `RangeEnumeration` class as defined below:

```java
package ssk.experiments;
import java.util.Enumeration;

public class RangeEnumeration implements Enumeration<Integer> {
    private Integer current = 0, max;
    public RangeEnumeration(int max) { this.max = max; }
    @Override
    public boolean hasMoreElements() { return current < max; }
    @Override
    public Integer nextElement() { return current++; }
}
```

Jython seamlessly handles the getting of an instance of an `Iterator` from a Java
[`Iterable`](https://docs.oracle.com/javase/8/docs/api/java/lang/Iterable.html). This is actually
how the `for` statement works with the `List` and `Set` collections discussed earlier (`Collection`
is a sub-interface of `Iterable`). 

## Patching Java Classes

In Python, new methods and attributes can be added to existing classes. This comes from the dynamic
nature of the programming language and the runtime. The JVM is also a dynamic runtime, but the Java
language doesn't allow us to modify existing classes. This is where Jython comes in. Jython lets us
add and override methods on existing Java classes. Although this is seldom needed, this can
illustrate the extent of Jython's integration with the JVM.

Here's a Java class:

```java
package ssk.experiments;
import java.util.List;

public class Country {
	private String name;
	public Country(String name) { this.name = name; }
	public String getName() { return name; }
	public void setName(String name) { this.name = name; }
}
```

There's nothing fancy with the above class. It's a regular class with one property with a `.get` and
`.set` methods. Now, let's add a new method to this class.

```python
from ssk.experiments import Country


def upcase(self):
	self.name = self.name.upper()


Country.upcase = upcase

# Create a `Country` object and call `upper_name` method.
largest_country = Country('Russia')
largest_country.upcase()
print largest_country.name
```

This would print `RUSSIA`, as expected.

Note that this is an advanced feature and should be used with caution. In almost all cases, it is
probably a better idea to modify the original Java class definition directly. But when that is not
an option, creating a simple Python function that works with these objects should be considered.
Modifying existing classes should only be used as a last resort.

## Operator Overloading

One nice and practical case for adding methods on existing Java classes is to leverage Python's
support for operator overloading with Java classes. One good example for this is with the
`BigDecimal` class. Mathematical operations on objects of `BigDecimal` are provided as individual
methods like `.add`, `.subtract` *etc*. We can add operator support  (in Jython) for these objects
by adding the appropriate methods to the `BigDecimal` class.

For instance, here's how we can add support for the `+` operator:

```python
from java.math import BigDecimal

BigDecimal.__add__ = lambda self, other: self.add(other)

print BigDecimal(42) + BigDecimal(10)
```

This would print `52`, as expected. More methods can be added to support all the mathematical
operators such as `__sub__` for subtraction and `__mul__` for multiplication *etc*. The full list of
such method names can be found on the official [data model documentation
page](http://www.jython.org/docs/reference/datamodel.html#emulating-numeric-types).

## Conclusion

This is not intended to be an exhaustive guide to what Jython can do. I hoped to give you a taste of
how well Jython handles inter-op with Java and hopefully I've helped you write better Python - Java
inter-op code. Thank you and any suggestions and feedback are very welcome.
