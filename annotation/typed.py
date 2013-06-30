# Written by Manuel Cerón

# Copyright Manuel Cerón.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

"""Tools for adding type annotations in Python.

This module provides a set of tools for type checking and annotations:

- typechecked() provides a decorator for checking the types in annotations.
- Interface provides a subclass to define structural interfaces.
- union() provides a group of types.
- predicate() provides type that checks a precondition.
"""

__author__ = ('Manuel Cerón <ceronman@gmail.com>')
__all__ = ['AnyType', 'Interface', 'only', 'optional', 'options', 'predicate',
           'typechecked', 'typedef', 'union']

import functools
import inspect

EMPTY_ANNOTATION = inspect.Signature.empty


class UnionMeta(type):
    """Metaclass for union types.

    An object is an instance of a union type if it is instance of any of the
    members of the union.

    >>> NumberOrString = union(int, str)
    >>> isinstance(1, NumberOrString)
    True
    >>> isinstance('string', NumberOrString)
    True
    >>> issubclass(int, NumberOrString)
    True
    >>> issubclass(str, NumberOrString)
    True
    """
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        types = getattr(cls, '__types__', None)
        if not isinstance(types, set):
            raise TypeError('Union requires a __types__ set')

        if any(not isinstance(t, type) for t in types):
            raise TypeError('Union __types__ elements must be type')
        return cls

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        return any(isinstance(instance, t) for t in cls.__types__)

    def __subclasscheck__(cls, subclass):
        """Override for isinstance(instance, cls)."""
        if isinstance(subclass, UnionMeta):
            return all(issubclass(t, cls) for t in subclass.__types__)
        return any(issubclass(subclass, t) for t in cls.__types__)

    def __repr__(cls):
        return '<union {0}>'.format(repr(cls.__types__))


def union(*args):
    """A convenience function for creating unions. See UnionMeta."""
    return UnionMeta('union', (), {'__types__': set(args)})


class AnyTypeMeta(type):
    """Metaclass for AnyType.

    Any object is instance of AnyType and any type is sublcass of anytype.

    >>> isinstance(1, AnyType)
    True
    >>> isinstance(None, AnyType)
    True
    >>> isinstance('string', AnyType)
    True
    >>> issubclass(int, AnyType)
    True
    >>> issubclass(str, AnyType)
    True
    >>> issubclass(None, AnyType)
    True
    """
    def __new__(mcls, name, bases, namespace):
        return super().__new__(mcls, name, bases, namespace)

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        return True

    def __subclasscheck__(cls, subclass):
        """Override for isinstance(instance, cls)."""
        return True


class AnyType(metaclass=AnyTypeMeta):
    """See AnyTypeMeta."""
    pass


def _implements_signature(function, signature):
    """True if the given function implements the given inspect.Signature."""
    try:
        instance_signature = inspect.signature(function)
    except TypeError:
        return False
    except ValueError: # we got a builtin.
        return True

    cls_params = signature.parameters.values()
    instance_params = instance_signature.parameters.values()
    if len(cls_params) != len(instance_params):
        return False

    for cls_param, instance_param in zip(cls_params, instance_params):
        if cls_param.name != instance_param.name:
            return False

        cls_annotation = cls_param.annotation
        instance_annotation = instance_param.annotation

        if cls_annotation is EMPTY_ANNOTATION:
            cls_annotation = AnyType

        if instance_annotation is EMPTY_ANNOTATION:
            instance_annotation = AnyType

        if not issubclass(cls_annotation, instance_annotation):
            return False


    cls_annotation = signature.return_annotation
    instance_annotation = instance_signature.return_annotation

    if cls_annotation is EMPTY_ANNOTATION:
        cls_annotation = AnyType

    if instance_annotation is EMPTY_ANNOTATION:
        instance_annotation = AnyType

    if not issubclass(instance_annotation, cls_annotation):
        return False
    return True


class InterfaceMeta(type):
    """Metaclass for an Interface.

    An interface defines a set methods and attributes that an object must
    implement. Any object implementing those will be considered an instance of
    the interface.

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
    >>> isinstance(iter([]), IterableWithLen)
    False
    >>> issubclass(list, IterableWithLen)
    True
    >>> issubclass(int, IterableWithLen)
    False
    >>> class Person(Interface):
    ...     name = str
    ...     age = int
    ...     def say_hello(name: str) -> str:
    ...             pass
    ...
    >>> class Developer:
    ...     def __init__(self, name, age):
    ...             self.name = name
    ...             self.age = age
    ...     def say_hello(self, name: str) -> str:
    ...             return 'hello ' + name
    ...
    >>> isinstance(Developer('dave', 20), Person)
    True
    """

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # TODO: check base classes, prevent multiple inheritance.
        cls.__signatures__ = {}
        cls.__attributes__ = {}
        for name, value in namespace.items():
            if name in ('__qualname__', '__module__', '__doc__'):
                continue
            if inspect.isfunction(value):
                mcls.add_method(cls, value)
                continue

            mcls.add_attribute(cls, name, value)
        return cls

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        for name, type_ in cls.__attributes__.items():
            try:
                attribute = getattr(instance, name)
            except AttributeError:
                return False

            if not isinstance(attribute, type_):
                return False

        for name, signature in cls.__signatures__.items():
            function = getattr(instance, name, None)
            if not _implements_signature(function, signature):
                return False
        return True

    def __subclasscheck__(cls, subclass):
        """Override for isinstance(instance, cls)."""
        if cls is subclass:
            return True

        # TODO: support attributes
        for name, signature in cls.__signatures__.items():
            try:
                function = inspect.getattr_static(subclass, name)
            except AttributeError:
                return False
            if isinstance(function, (staticmethod, classmethod)):
                return False
            try:
                subclass_signature = inspect.signature(function)
            except TypeError:
                return False
            except ValueError: # we probably got a builtin
                return True

            cls_params = list(signature.parameters.values())
            subclass_params = list(subclass_signature.parameters.values())

            subclass_params.pop(0) # remove 'self'

            if len(cls_params) != len(subclass_params):
                return False

            for cls_param, instance_param in zip(cls_params, subclass_params):
                if cls_param.name != instance_param.name:
                    return False

                cls_annotation = cls_param.annotation
                instance_annotation = instance_param.annotation

                if cls_annotation is EMPTY_ANNOTATION:
                    cls_annotation = AnyType

                if instance_annotation is EMPTY_ANNOTATION:
                    instance_annotation = AnyType

                if not issubclass(cls_annotation, instance_annotation):
                    return False


            cls_annotation = signature.return_annotation
            instance_annotation = subclass_signature.return_annotation

            if cls_annotation is EMPTY_ANNOTATION:
                cls_annotation = AnyType

            if instance_annotation is EMPTY_ANNOTATION:
                instance_annotation = AnyType

            if not issubclass(instance_annotation, cls_annotation):
                return False
        return True

    def add_method(cls, method):
        """Adds a new method to an Interface."""
        # TODO check that signatures contain only types as annotations.
        try:
            cls.__signatures__[method.__name__] = inspect.signature(method)
        except (TypeError, AttributeError):
            raise TypeError('Interface methods should have a signature')
        return method

    def add_attribute(cls, name, type_=AnyType):
        """Adds a new attribute to an Interface."""
        if not isinstance(type_, type):
            # TODO the error message below is incomplete.
            raise TypeError('Interface attributes should be type')
        cls.__attributes__[name] = type_


class Interface(metaclass=InterfaceMeta):
    """See InterfaceMeta."""
    pass


class PredicateMeta(type):
    """Metaclass for a predicate.

    An object is an instance of a predicate if applying the predicate to the
    object returns True.

    >>> Positive = predicate(lambda x: x > 0)
    >>> isinstance(1, Positive)
    True
    >>> isinstance(0, Positive)
    False
    """
    def __new__(mcls, name, bases, namespace):
        return super().__new__(mcls, name, bases, namespace)

    def __instancecheck__(cls, instance):
        try:
            return cls.__predicate__(instance)
        except AttributeError:
            return False

    def __subclasscheck__(cls, subclass):
        return False


def predicate(function, name=None):
    """Convenience function to create predicates. See PredicateMeta.

    >>> Even = predicate(lambda x: x % 2 == 0)
    >>> isinstance(2, Even)
    True
    >>> isinstance(1, Even)
    False
    """
    name = name or function.__name__
    return PredicateMeta(name, (), {'__predicate__': function})


def optional(type_):
    """Optional type predicate. An object can be None or the specified type.

    >>> isinstance(1, optional(int))
    True
    >>> isinstance(None, optional(int))
    True
    """
    return predicate(lambda x: (x is None or isinstance(x, type_)), 'optional')


def typedef(function):
    """A type representing a given function signature.

    It should be used as decorator:

    >>> @typedef
    ... def callback(a: int) -> int:
    ...     pass
    ...
    >>> def handler(a: int) -> int:
    ...     return a
    ...
    >>> isinstance(handler, callback)
    True
    >>> isinstance(lambda x: x, callback)
    False
    """
    signature = inspect.signature(function)
    return predicate(lambda x: _implements_signature(x, signature), 'typedef')


def options(*args):
    """A predicate type for a set of predefined values.

    >>> Days = options('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
    >>> isinstance('mon', Days)
    True
    >>> isinstance('other', Days)
    False
    """
    return predicate(lambda x: x in args, 'options')


def only(type_):
    """A predicate requiring an exact type, not super classes.

    >>> isinstance(True, only(bool))
    True
    >>> isinstance(1, only(bool))
    False
    """
    return predicate(lambda x: type(x) is type_, 'only')


def _check_argument_types(signature, *args, **kwargs):
    """Check that the arguments of a function match the given signature."""
    bound_arguments = signature.bind(*args, **kwargs)
    parameters = signature.parameters
    for name, value in bound_arguments.arguments.items():
        annotation = parameters[name].annotation
        if annotation is EMPTY_ANNOTATION:
            annotation = AnyType
        if not isinstance(value, annotation):
            raise TypeError('Incorrect type for "{0}"'.format(name))


def _check_return_type(signature, return_value):
    """Check that the return value of a function matches the signature."""
    annotation = signature.return_annotation
    if annotation is EMPTY_ANNOTATION:
        annotation = AnyType
    if not isinstance(return_value, annotation):
        raise TypeError('Incorrect return type')
    return return_value


def typechecked(target):
    """A decorator to make a function check its types at runtime.

    >>> @typechecked
    ... def test(a: int):
    ...     return a
    ...
    >>> test(1)
    1
    >>> test('string')
    Traceback (most recent call last):
        ...
    TypeError: Incorrect type for "a"
    """
    signature = inspect.signature(target)

    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        _check_argument_types(signature, *args, **kwargs)
        return _check_return_type(signature, target(*args, **kwargs))
    return wrapper

if __name__ == '__main__':
    import doctest
    doctest.testmod()
