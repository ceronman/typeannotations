import unittest

from annotation.overload import AmbiguousFunction, FunctionNotFound, overloaded


class TestOverloaded(unittest.TestCase):
    def test_creation(self):
        @overloaded
        def foo():
            return 'no args'
        
        @overloaded
        def foo(a, b):
            return 'two empty args'
        
        @overloaded
        def foo(a:int, b):
            return 'one int'
        
        @overloaded
        def foo(a:int, b:str):
            return 'int and str'
        
        def other_foo(a:str, b:int):
            return 'str and int'
        foo.add_function(other_foo)
        
        self.assertEqual(foo(), 'no args')
        self.assertEqual(foo(object(), object()), 'two empty args')
        self.assertEqual(foo(1, object()), 'one int')
        self.assertEqual(foo(1, ''), 'int and str')
        self.assertEqual(foo('', 1), 'str and int')
        self.assertRaises(FunctionNotFound, foo, object(), object(), object())

        def bar(*args):
            pass
        
        def baz(**kwargs):
            pass
        
        self.assertRaises(TypeError, overloaded, bar)
        self.assertRaises(TypeError, overloaded, baz)
    
    def test_ambiguous(self):
        @overloaded
        def foo():
            pass
        
        def other_foo():
            pass
        
        self.assertRaises(AmbiguousFunction, foo.add_function, other_foo)

        @overloaded
        def foo(a:int, b):
            pass
        
        def other_foo(a, b:int):
            pass
        
        self.assertRaises(AmbiguousFunction, foo.add_function, other_foo)


if __name__ == '__main__':
    unittest.main()
