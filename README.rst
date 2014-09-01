Type annotations for Python
===========================

https://github.com/ceronman/typeannotations


About
-----

The ``typeannotations`` module provides a set of tools for type checking and
type inference of Python code. It also a provides a set of types useful for
annotating functions and objects.

These tools are mainly designed to be used by static analyzers such as linters,
code completion libraries and IDEs. Additionally, decorators for making
run-time checks are provided. Run-time type checking is not always a good
idea in Python, but in some cases it can be very useful.


Run-time type checking.
-----------------------

The ``typechecked`` decorator can be used to check types specified in function
annotations. For example:

.. code-block:: pycon

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


Structural interfaces
---------------------

The ``Interface`` class allows you to define interfaces that are checked
dynamically. You don't have to explicitly indicate when an object or class
implements a given ``Interface``. If an object provides the methods and
attributes specified in the ``Interface``, it's considered a valid
implementation.

For example, let's define a simple interface:

.. code-block:: pycon

   >>> class Person(Interface):
   ...     name = str
   ...     age = int
   ...     def say_hello(name: str) -> str:
   ...             pass

Any object defining those the ``name``, ``age`` and ``say_hello()`` members is
a valid implementation of that interface. For example:

.. code-block:: pycon

   >>> class Developer:
   ...     def __init__(self, name, age):
   ...             self.name = name
   ...             self.age = age
   ...     def say_hello(self, name: str) -> str:
   ...             return 'hello ' + name
   ...
   >>> isinstance(Developer('bill', 20), Person)
   True

This also works with built-in types:

.. code-block:: pycon

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


Typedefs
''''''''

A ``typedef`` is similar to an ``Interface`` except that it defines a single
function signature. This is useful for defining callbacks. For example:

.. code-block:: pycon

   >>> @typedef
   ... def callback(event: Event) -> bool:
   ...     pass
   ...

Then it's possible to check if a function implements the same signature:

.. code-block:: pycon

   >>> def handler(event: MouseEvent) -> bool:
   ...     print('click')
   ...     return True
   ...
   >>> isinstance(handler, callback)
   True
   >>> isinstance(lambda: True, callback)
   False

Note that ``MouseEvent`` is a subclass of ``Event``.


Type unions
-----------

A ``union`` is a collection of types and it's a type itself. An object is an
instance of a ``union`` if it's an instance of any of the elements in the union.
For example:

.. code-block:: pycon

   >>> NumberOrString = union(int, str)
   >>> isinstance(1, NumberOrString)
   True
   >>> isinstance('string', NumberOrString)
   True
   >>> issubclass(int, NumberOrString)
   True
   >>> issubclass(str, NumberOrString)
   True


Predicates
----------

A ``predicate`` is a special type defined by a function that takes an object
and returns ``True`` or ``False`` indicating if the object implements the type.
For example:

.. code-block:: pycon

   >>> Positive = predicate(lambda x: x > 0)
   >>> isinstance(1, Positive)
   True
   >>> isinstance(0, Positive)
   False

Predicates can also be defined using a decorator:

.. code-block:: pycon

   >>> @predicate
   ... def Even(object):
   ...     return object % 2 == 0

Predicates can also be combined using the `&`` operator:

.. code-block:: pycon

   >>> EvenAndPositive = Even & Positive

Predicates are useful for defining contracts:

.. code-block:: pycon

   >>> Positive = predicate(lambda x: x > 0)
   >>> @typechecked
   ... def sqrt(n: Positive):
   ...     ...
   >>> sqrt(-1)
   Traceback (most recent call last):
     ...
   TypeError: Incorrect type for "n"


The ``optional`` predicate
''''''''''''''''''''''''''

The ``optional`` predicate indicates that the object must be from the given type
or `None`. For example:

.. code-block:: pycon

   >>> isinstance(1, optional(int))
   True
   >>> isinstance(None, optional(int))
   True

And checking types at runtime:

.. code-block:: pycon

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


The ``only`` predicate
''''''''''''''''''''''

The ``only`` predicate indicates that an object can **only** be of the specified
type, and not of any of its super classes. For example:

.. code-block:: pycon

   >>> isinstance(True, only(bool))
   True
   >>> isinstance(1, only(bool))
   False

Note that in Python `bool` is a sublcass of `int`.


The ``options`` predicate
'''''''''''''''''''''''''

The ``options`` predicate indicates that the value of an object must be one of
the given options. For example:

.. code-block:: pycon

   >>> FileMode = options('r', 'w', 'a', 'r+', 'w+', 'a+')
   >>> isinstance('w', FileMode)
   True
   >>> isinstance('x', FileMode)
   False

This is useful when defining a function:

.. code-block:: pycon

   >>> @typecheck
   ... def open(filename: str, mode: options('w', 'a')):
   ...		...


Complex Types:
''''''''''''''

Complex types are also accepted in both interfaces and type specifications.

.. code-block:: pycon

   >>> @typechecked
   ... def test(a: { int: ( str, bool ) }) -> (bool, int):
   ...     return isinstance(a, dict), len(a)
   ...
   >>> test({ 1: ('a', False) })
   (True, 1)
   >>> test('string')
   Traceback (most recent call last):
      ...
   TypeError: Incorrect type for "a"

The rules are:

1. A list of types.  The value must be a list containing only the specified
   types.
2. A set of types.  The value must be a set containing only the specified types.
3. A tuple of types.  The value must be a tuple containing the specified types in the specified
   order.
4. A dict of types.  The value must be a dict where each (key, value) pair is
   assocated with a (key, value) pair in the type dictionary.

Any of the complex types can nest and contain any other type.



To be implemented:
------------------

Function overloading
''''''''''''''''''''

.. code-block:: python

   @overload
   def isinstance(object, t: type):
       ...

   @overload
   def isinstance(object, t: tuple):
       ...

Annotate existing functions and libraries
'''''''''''''''''''''''''''''''''''''''''

.. code-block:: python

   @annotate('builtins.open')
   def open_annotated(file: str,
                      mode: options('r', 'w', 'a', 'r+', 'w+', 'a+'),
                      buffering: optional(int)) -> IOBase:
       pass


License
-------

| Licensed under the Apache License, Version 2.0 (the "License");
| you may not use this file except in compliance with the License.
| You may obtain a copy of the License at
| 
| http://www.apache.org/licenses/LICENSE-2.0
| 
| Unless required by applicable law or agreed to in writing, software
| distributed under the License is distributed on an "AS IS" BASIS,
| WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
| either express or implied.  See the License for the specific language
| governing permissions and limitations under the License.
