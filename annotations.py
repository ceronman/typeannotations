import functools
import inspect

def _get_argument_value(name, spec, args, kwargs):
    position = spec.args.index(name)
    try:
        return args[position]
    except IndexError:
        return kwargs[name]


def annotate(target):
    spec = inspect.getfullargspec(target)

    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        for name in spec.args:
            value = _get_argument_value(name, spec, args, kwargs)
            value_type = spec.annotations.get(name)
            if value_type is not None and not isinstance(value, value_type):
                raise AttributeError('Incorrect type for "{0}"'.format(name))
        return_value = target(*args, **kwargs)
        return_type = spec.annotations.get('return')
        if (return_type is not None
                and not isinstance(return_value, return_type)):
            raise RuntimeError('The function returned incorrect type.')
        return return_value
    return wrapper

@annotate
def test_function(one: str, two: int, three: float, four:bool) -> int:
    print(one, two, three, four)
    return 'hello'


if __name__ == '__main__':
    print(test_function('str', 1, 2.5, four=True))
