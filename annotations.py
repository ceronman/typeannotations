import functools
import inspect


EMPTY_ANNOTATION = inspect.Signature.empty


class UnionMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        types = getattr(cls, '__types__', None)
        if not isinstance(types, set):
            raise TypeError('Union requires a __types__ set')

        if any(not isinstance(t, type) for t in types):
            raise TypeError('Union __types__ elements must be type')
        return cls

    def __instancecheck__(cls, instance):
        return any(isinstance(instance, t) for t in cls.__types__)

    def __subclasscheck__(cls, subclass):
        if isinstance(subclass, UnionMeta):
            return all(issubclass(t, cls) for t in subclass.__types__)
        return any(issubclass(subclass, t) for t in cls.__types__)

    def __repr__(cls):
        return '<union {0}'.format(repr(cls.__types__))


class AnyTypeMeta(type):
    def __new__(mcls, name, bases, namespace):
        return super().__new__(mcls, name, bases, namespace)

    def __instancecheck__(cls, instance):
        return True

    def __subclasscheck__(cls, subclass):
        return True

class AnyType(metaclass=AnyTypeMeta):
    pass


def union(*args):
    return UnionMeta('Union', (), {'__types__': set(args)})


class InterfaceMeta(type):

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # TODO: check base classes, prevent multiple inheritance.
        # TODO: check signatures to prevent non type annotations.
        signatures = {}
        for name, value in namespace.items():
            try:
                signatures[name] = inspect.signature(value)
            except TypeError:
                pass
            # TODO, check properties
        cls.__signatures__ = signatures
        return cls

    def __instancecheck__(cls, instance):
        for name, signature in cls.__signatures__.items():
            try:
                function = getattr(instance, name)
            except AttributeError:
                return False
            try:
                instance_signature = inspect.signature(function)
            except TypeError:
                return False
            except ValueError: # we probably got a builtin
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

            return issubclass(instance_annotation, cls_annotation)



class Interface(metaclass=InterfaceMeta):
    pass


def _check_argument_types(signature, *args, **kwargs):
    bound_arguments = signature.bind(*args, **kwargs)
    parameters = signature.parameters
    for name, value in bound_arguments.arguments.items():
        annotation = parameters[name].annotation
        if annotation is EMPTY_ANNOTATION:
            annotation = AnyType
        if not isinstance(value, annotation):
            raise TypeError('Incorrect type for "{0}"'.format(name))


def _check_return_type(signature, return_value):
    annotation = signature.return_annotation
    if annotation is EMPTY_ANNOTATION:
        annotation = AnyType
    if not isinstance(return_value, annotation):
        raise TypeError('Incorrect return type')
    return return_value

def typechecked(target):
    signature = inspect.signature(target)

    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        _check_argument_types(signature, *args, **kwargs)
        return _check_return_type(signature, target(*args, **kwargs))
    return wrapper
