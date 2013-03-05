# Type annotations for Python

https://github.com/ceronman/typeannotations

## About

The `typeannotations` module provides a set of tools for type checking and type
inference of Python code. It also a provides a set of types useful for
annotating functions and objects.

This tools are mainly designed to be used by static analyzers such as linters,
code completion libraries and IDEs. Additionally, decorators for making
run-time checks are provided too. Run-time type checking is not always a good
idea in Python, however, in some cases can be very useful.

## Run-time type checking.

The `typechecked` decorator can be used to check types specified in function
annotations. For example:

```python
>>> @typechecked
... def test(a: int) -> int:
...     return a
...
>>> test(1)
1
>>> test('string')
Traceback (most recent call last):
   ...
TypeError: Incorrect type for "a"
```

## Structural interfaces

The `Interface` class allows you to define interfaces that are checked
dynamically. You don't have to explicitly indicate when an object or class
implements a given `Interface`. If an object provides the methods and
attributes specified in the `Interface`, it's considered a valid
implementation.

For example, let's define a simple interface:

```python
>>> class Person(Interface):
    ...     name = str
    ...     age = int
    ...     def say_hello(name: str) -> str:
    ...             pass
```

Any object defining those the `name`, `age` and `say_hello()` members is a
valid implementation of that interface. For example:

```python
>>> class Developer:
...     def __init__(self, name, age):
...             self.name = name
...             self.age = age
...     def say_hello(self, name: str) -> str:
...             return 'hello ' + name
...
>>> isinstance(Developer('bill', 20), Person)
True
```

This also works with built-in types:

```python
>>> class IterableWithLen(Interface):
...     def __iter__():
...             pass
...     def __len__():
...             pass
...
>>> isinstance([], IterableWithLen)
True
>>> isinstance({}, IterableWithLen)
True
>>> isinstance(1, IterableWithLen)
False
```

### Typedefs

A `typedef` is similar to an `Interface` except that it defines a single
function signature. This is useful for defining callbacks. For example:

```python
>>> @typedef
... def callback(event: Event) -> bool:
...     pass
...
```

Then it's possible to check if a function implements the same signature:

```python
>>> def handler(event: MouseEvent) -> bool:
...     print('click')
...     return True
...
>>> isinstance(handler, callback)
True
>>> isinstance(lambda: True, callback)
False
```

Note that `MouseEvent` is a subclass of `Event`.

## Type unions

A `union` is a collection of types and it's a type it self. An object is an
instance of an `union` if it's an instance of any of the elements in the union.
For example:

```python
>>> NumberOrString = union(int, str)
>>> isinstance(1, NumberOrString)
True
>>> isinstance('string', NumberOrString)
True
>>> issubclass(int, NumberOrString)
True
>>> issubclass(str, NumberOrString)
True
```

## Predicates

A `predicate` is a special type defined by a function that takes an object and
returns `True` or `False` indicating if the object implements the type. For
example:

```python
>>> Positive = predicate(lambda x: x > 0)
>>> isinstance(1, Positive)
True
>>> isinstance(0, Positive)
False
```

Predicates can also be defined using a decorator:

```python

>>> @predicate
... def Even(object):
...     return object % 2 == 0
```

Predicates can also be combined using the `&` operator:

```python
>>> EvenAndPositive = Even & Positive
```

Predicates are useful for defining contracts:

```python
>>> Positive = predicate(lambda x: x > 0)
>>> @typechecked
... def sqrt(n: Positive):
...     ...
>>> sqrt(-1)
Traceback (most recent call last):
	...
TypeError: Incorrect type for "n"
```

### The `optional` predicate

The `optional` predicate indicates that the object must be from the given type
or `None`. For example:

```python
>>> isinstance(1, optional(int))
True
>>> isinstance(None, optional(int))
True
```

And checking types at runtime:

```python
>>> @typechecked
... def greet(name: optional(str) = None):
...     if name is None:
...             print('hello stranger')
...     else:
...             print('hello {0}'.format(name))
...
>>> greet()
hello stranger
>>> greet('bill')
hello bill
```

### The `only` predicate

The `only` predicate indicates that an object can **only** be of the specified
type, and not of any of its super classes. For example:

```python
>>> isinstance(True, only(bool))
True
>>> isinstance(1, only(bool))
False
```

Note that in Python `bool` is a sublcass of `int`.


### The `options` predicate

The `options` predicate indicates that the value of an object must be one of
the given options. For example:

```python
>>> FileMode = options('r', 'w', 'a', 'r+', 'w+', 'a+')
>>> isinstance('w', FileMode)
True
>>> isinstance('x', FileMode)
False
```

This is useful when defining a function:

```python
>>> @typecheck
... def open(filename: str, mode: options('w', 'a')):
...		...
```

## To be implemented:

### Collections definitions:

```python
typedict({str: int})
typeseq([int])
typeseq(set(int))
typeseq((int,))
...
```

### Function overloading

```python
@overload
def isinstance(object, t: type):
	...

@overload
def isinstance(object, t: tuple):
	...
```

### Annotate existing functions and libraries

```python
@annotate('builtins.open')
def open_annotated(file: str,
				   mode: options('r', 'w', 'a', 'r+', 'w+', 'a+'),
				   buffering: optional(int)) -> IOBase:
	pass
```

## License

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.  See the License for the specific language
governing permissions and limitations under the License.
```
