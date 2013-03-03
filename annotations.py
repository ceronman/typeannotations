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
        cls.__signatures__ = {}
        cls.__attributes__ = {}
        for name, value in namespace.items():
            if name in ('__qualname__', '__module__', 'set_something'):
                continue

            if inspect.isfunction(value):
                mcls.add_method(cls, value)
                continue

            mcls.add_attribute(cls, name, value)
        return cls

    def __instancecheck__(cls, instance):
        for name, type_ in cls.__attributes__.items():
            try:
                attribute = getattr(instance, name)
            except AttributeError:
                return False

            if attribute is not None and not isinstance(attribute, type_):
                return False

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

            if not issubclass(instance_annotation, cls_annotation):
                return False
        return True

    def __subclasscheck__(cls, subclass):
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
        # TODO check that signatures contain only types as annotations.
        try:
            cls.__signatures__[method.__name__] = inspect.signature(method)
        except (TypeError, AttributeError):
            raise TypeError('Interface methods should have a signature')
        return method

    def add_attribute(cls, name, type_=AnyType):
        if not isinstance(type_, type):
            raise TypeError('Interface attributes should be type')
        cls.__attributes__[name] = type_


class Interface(metaclass=InterfaceMeta):
    pass


def _check_argument_types(signature, *args, **kwargs):
    bound_arguments = signature.bind(*args, **kwargs)
    parameters = signature.parameters
    for name, value in bound_arguments.arguments.items():
        if value is None:
            continue
        annotation = parameters[name].annotation
        if annotation is EMPTY_ANNOTATION:
            annotation = AnyType
        if not isinstance(value, annotation):
            raise TypeError('Incorrect type for "{0}"'.format(name))


def _check_return_type(signature, return_value):
    if return_value is None:
        return
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
