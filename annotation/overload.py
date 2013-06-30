# Copyright 2013 Moritz Sichert
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

import collections
import inspect


_empty_func = lambda *args: None
_empty_annotation = inspect.Parameter.empty


def _ann_cmp(ann1, ann2):
    """
    Compares two annotations and returns True if ann1 is more specific
    than ann2.
    """
    return ann1 != ann2 and (ann2 == _empty_annotation or issubclass(ann1, ann2))


def _get_annotations(func):
    return (param.annotation for param in inspect.signature(func).parameters.values())


def _func_eq(func1, func2):
    """
    Returns True if the two functions's signatures evaluate to the same types.

    Arguments:
    func1, func2: Functions that are supported by inspect.signature.
                  Both must have same number of arguments.
    """
    # That's how the algorithm works:
    # First check if the functions aren't equal (obvious).
    # Then check if the annotations aren't all equal, too.
    # 
    # Now basically we create a table with following structure:
    # 
    #                             | annotation1 | annotation2 | annot3 | ...
    # ------------------------------------------------------------------------
    # #1 | _ann_cmp(func1, func2) |    True     |    False    |  False | ...
    # #2 | _ann_cmp(func2, func1) |    False    |    False    |  True  | ...
    # #3 | func1 == func2         |    False    |    True     |  False | ...
    # 
    # funcN means: "Take funcN's Mth annotation" where M is the number shown in
    # the column caption.
    # 
    # First we get rid of all columns with True in row #3. We also don't need
    # row #3 anymore.
    # 
    #    | annotation1 | annotation3 | ...
    # --------------------------------------
    # #1 |    True     |    False    | ...
    # #2 |    False    |    True     | ...
    # 
    # Then we generate a new row called #1+2 by combining #1 and #2 with
    # logical or
    # 
    #      | annotation1 | annotation3 | ...
    # ----------------------------------------
    # #1   |    True     |    False    | ...
    # #2   |    False    |    True     | ...
    # #1+2 |    True     |    True     | ...
    # 
    # The last step is to check if #1+2 is equal with #1 or #2. If it is,
    # return False, otherwise return True.
    # 
    # Why does it work?
    # #TODO
    if func1 == func2:
        return True
    if func1 == _empty_func or func2 == _empty_func:
        return False
    # grab all annotations
    # annotations = [[func1ann1, func2ann1], [func1ann2, func2ann2], ...]
    annotations = tuple(zip(*[_get_annotations(func) for func in (func1, func2)]))
    if all(ann1 == ann2 for ann1, ann2 in annotations):
        return True
    # generate #1 and #2 and leave out the ones with True in #3
    annotations = [(_ann_cmp(ann1, ann2), _ann_cmp(ann2, ann1)) for ann1, ann2 in annotations if ann1!=ann2]
    # calculate #1+2
    annotations_combined = tuple(ann1 or ann2 for ann1, ann2 in annotations)
    return annotations_combined not in zip(*annotations)


def _func_cmp(func1, func2):
    """
    Compares two functions by their signatures.

    Arguments:
    func1, func2: Functions that are supported by inspect.signature.
                  Both must have same number of arguments.

    Returns:
    True if func1's argument annotation types have stronger or as strong types
    than func2's ones.
    False else.
    """
    if func1 == func2:
        return False
    if func1 == _empty_func:
        return False
    elif func2 == _empty_func:
        return True
    for ann1, ann2 in zip(*[_get_annotations(func) for func in (func1, func2)]):
        if ann1 == ann2:
            continue
        if ann2 == _empty_annotation:
            continue
        if not issubclass(ann1, ann2):
            return False
    return True


def _check_func_types(func, types):
    return all((typ == ann) or issubclass(typ, ann) for typ, ann in zip(types, _get_annotations(func)) if ann != _empty_annotation)


class AmbiguousFunction(ValueError):
    """
    Gets raised if trying to add a function to a FunctionHeap if an equivalent
    one is already in it.
    """
    def __init__(self, func):
        ValueError.__init__(self,
            'function {0} is ambiguous with an existing one'.format(func))


class FunctionNotFound(Exception):
    """
    Gets raised if a function with given types couldn't be found.
    """
    pass


class FunctionHeap(object):
    def __init__(self, func):
        self._root = func
        self._childs = set()

    def push(self, func):
        if _func_eq(func, self._root):
            raise AmbiguousFunction(func)
        if self._root == _empty_func:
            if all(_func_cmp(child._root, func) for child in self._childs):
                self._root = func
        elif _func_cmp(func, self._root):
            if any(_func_eq(func, child._root) for child in self._childs):
                raise AmbiguousFunction(func)
            for child in self._childs:
                if _func_cmp(func, child._root):
                    child.push(func)
                    return
            self._childs.add(self.__class__(func))
        else:
            old_heap = self.__class__(self._root)
            old_heap._childs = self._childs
            if _func_cmp(self._root, func):
                self._root = func
                self._childs = set([old_heap])
            else:
                new_heap = self.__class__(func)
                self._root = _empty_func
                self._childs = set([old_heap, new_heap])

    def find(self, types):
        """
        Finds the most specialized function for args.
        For example if args where (1,2,'foo', 'bar') and the Heap had the childs
        foo(a:int,b,c,d) and bar(a:int,b,c:str,d) it would choose bar.

        Arguments:
        *args: all types that the function should accept
        """
        if self._root != _empty_func and not _check_func_types(self._root, types):
            raise FunctionNotFound()
        current_heap = self
        new_root = True
        while new_root:
            new_root = False
            for child in current_heap._childs:
                if _check_func_types(child._root, types):
                    current_heap = child
                    new_root = True
        if current_heap._root == _empty_func:
            raise FunctionNotFound()
        return current_heap._root


class OverloadedFunction(collections.Callable):
    def __init__(self, module, name):
        self._module = module
        self._name = name
        self._functions = {} # {arg_len: FunctionHeap, ...}
        self._function_cache = {} # {(type1, type2, ...): func, ...}
    
    def add_function(self, func):
        parameters = inspect.signature(func).parameters
        for param in parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                raise TypeError('functions with *args and **kwargs are not supported')
        if len(parameters) not in self._functions:
            self._functions[len(parameters)] = FunctionHeap(func)
        else:
            self._functions[len(parameters)].push(func)
        self._function_cache = {}
    
    def __call__(self, *args):
        types = tuple(type(arg) for arg in args)
        if types in self._function_cache:
            return self._function_cache[types](*args)
        if len(args) not in self._functions:
            raise FunctionNotFound('No function found for signature: {0}'.format(types))
        else:
            func = self._functions[len(args)].find(types)
            self._function_cache[types] = func
            return func(*args)


_overloaded_functions = {} # {'module': {'function_name': OverloadedFunction, ...}, ...}


def overloaded(func):
    """
    Decorator that lets you declare the same function various times with
    different type annotations.
    """
    module = func.__module__
    qualname = func.__qualname__
    if module not in _overloaded_functions:
        _overloaded_functions[module] = {}
    if qualname not in _overloaded_functions[module]:
        _overloaded_functions[module][qualname] = OverloadedFunction(module, qualname)
    _overloaded_functions[module][qualname].add_function(func)
    return _overloaded_functions[module][qualname]
