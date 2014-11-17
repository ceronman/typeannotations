import unittest
from collections import namedtuple

from annotation.typed import (typechecked, Interface, union, AnyType, predicate,
    optional, typedef, options, only)



class TypecheckedTest(unittest.TestCase):

    def test_single_argument_with_builtin_type(self):

        @typechecked
        def test(a: int):
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, 'string')
        self.assertRaises(TypeError, test, 1.2)

    def test_single_argument_with_class(self):

        class MyClass:
            pass

        @typechecked
        def test(a: MyClass):
            return a

        value = MyClass()
        self.assertEqual(value, test(value))
        self.assertRaises(TypeError, test, 'string')

    def test_single_argument_with_subclass(self):

        class MyClass: pass
        class MySubClass(MyClass): pass

        @typechecked
        def test(a: MyClass):
            return a

        value = MySubClass()
        self.assertEqual(value, test(value))
        self.assertRaises(TypeError, test, 'string')

    def test_single_argument_with_union_annotation(self):
        from decimal import Decimal

        @typechecked
        def test(a: union(int, float, Decimal)):
            return a

        self.assertEqual(1, test(1))
        self.assertEqual(1.5, test(1.5))
        self.assertEqual(Decimal('2.5'), test(Decimal('2.5')))
        self.assertRaises(TypeError, test, 'string')

    def test_single_argument_with_predicate_annotation(self):

        @typechecked
        def test(a: predicate(lambda x: x > 0)):
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, 0)

    def test_single_argument_with_optional_annotation(self):

        @typechecked
        def test(a: optional(int)):
            return a

        self.assertEqual(1, test(1))
        self.assertEqual(None, test(None))

    def test_single_argument_with_typedef_annotation(self):

        @typedef
        def callback(a: int, b: str) -> dict:
            pass

        @typechecked
        def test(a: callback):
            return a(1, 'string')

        def f1(a: int, b: str) -> dict:
            return {}

        def f2(a: str, b: str):
            pass

        self.assertEqual({}, test(f1))
        self.assertRaises(TypeError, test, f2)

    def test_single_argument_with_options_annotation(self):

        @typechecked
        def test(a: options('open', 'write')):
            return a

        self.assertEqual('open', test('open'))
        self.assertEqual('write', test('write'))
        self.assertRaises(TypeError, test, 'other')

    def test_single_argument_with_only_annotation(self):

        @typechecked
        def test(a: only(int)):
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, True)

    def test_single_argument_with_interface(self):

        class Test(Interface):
            def test():
                pass

        class TestImplementation:
            def test(self):
                return 1

        class Other: pass

        @typechecked
        def test(a: Test):
            return 1

        self.assertEqual(1, test(TestImplementation()))
        self.assertRaises(TypeError, test, Other())

    def test_single_argument_with_no_annotation(self):

        @typechecked
        def test(a):
            return a

        self.assertEqual(1, test(1))
        self.assertEqual(1.5, test(1.5))
        self.assertEqual('string', test('string'))

    def test_multiple_arguments_with_annotations(self):

        @typechecked
        def test(a: int, b: str):
            return a, b

        self.assertEqual((1, 'string'), test(1, 'string'))
        self.assertRaises(TypeError, test, 1, 1)
        self.assertRaises(TypeError, test, 'string', 'string')
        self.assertRaises(TypeError, test, 'string', 1)

    def test_single_argument_with_none_value(self):

        @typechecked
        def test(a: int):
            return a

        self.assertRaises(TypeError, test, None)

    def test_multiple_arguments_some_with_annotations(self):

        @typechecked
        def test(a, b: str):
            return a, b

        self.assertEqual((1, 'string'), test(1, 'string'))
        self.assertEqual(('string', 'string'), test('string', 'string'))
        self.assertRaises(TypeError, test, 1, 1)
        self.assertRaises(TypeError, test, 'string', 1)

    def test_return_with_builtin_type(self):

        @typechecked
        def test(a) -> int:
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, 'string')
        self.assertRaises(TypeError, test, 1.2)

    def test_return_with_class(self):

        class MyClass:
            pass

        @typechecked
        def test1() -> MyClass:
            return MyClass()

        @typechecked
        def test2() -> MyClass:
            return 1

        self.assertIsInstance(test1(), MyClass)
        self.assertRaises(TypeError, test2)

    def test_return_with_sublass(self):

        class MyClass: pass
        class MySubClass(MyClass): pass

        @typechecked
        def test1() -> MyClass:
            return MySubClass()

        @typechecked
        def test2() -> MyClass:
            return 1

        self.assertIsInstance(test1(), MyClass)
        self.assertRaises(TypeError, test2)

    def test_return_with_union(self):

        @typechecked
        def test(a) -> union(int, float):
            return a

        self.assertEqual(1, test(1))
        self.assertEqual(1.1, test(1.1))
        self.assertRaises(TypeError, test, 'string')

    def test_return_with_interface(self):

        class Test(Interface):
            def test():
                pass

        class TestImplementation:
            def test(self):
                return 1

        class Other: pass

        @typechecked
        def test1() -> Test:
            return TestImplementation()

        @typechecked
        def test2() -> Test:
            return 1

        self.assertIsInstance(test1(), TestImplementation)
        self.assertRaises(TypeError, test2)

    def test_return_with_none_value(self):

        @typechecked
        def test(a) -> int:
            return a

        self.assertRaises(TypeError, test, None)

    def test_complex_types(self):
        simple_types = [ 'a', 1, None, 1.1, False ]
        check = namedtuple('check', ('test', 'good', 'bad'))

        checks = [
            check(
                [ str ],
                [ [ 'a' ], [ 'b', 'c' ], [ ], ],
                [ [ 1 ], [ 'a', 1 ] ]
            ),
            check(
                [ str, int ],
                [ [ 'a', 1 ], [ 'b', 'c', 1 ], [ 1 ], [ ], ],
                [ [ None ], [ 1, 'a', 1.1 ], [ 1, 1.1 ] ]
            ),
            check(
                [ ],
                [ [ 'a' ], [ 'b', 'c' ], [ ], ],
                [ ]
            ),
            check(
                ( str, int ),
                [ ( 'a', 1 ) ],
                [ ( 'a', 1, 2 ), tuple() ]
            ),
            check(
                { str: int },
                [ { 'a': 1 }, { 'a': 1, 'b': 2 }, { }, ],
                [ { 'a': None }, { 'a': 1, 1: 2 }, ]
            ),
            check(
                { str: int, int: int },
                [ { 'a': 1 }, { 'a': 1, 'b': 2 }, { 1: 1 }, { 'a': 1, 2: 2 }, { } ],
                [ { 'a': None }, { 1: 'a' }, { 'a': 1, 1: 'a' }, ]
            ),
            check(
                { },
                [ { 'a': 1 }, { 'a': 1, 'b': 2 }, { }, ],
                [ ]
            ),
            check(
                { str },
                [ { 'a', 'b' }, { 'a' }, set() ],
                [ { 1 }, { 'a', False } ]
            ),
            check(
                { str, int },
                [ { 1 }, { 'a', 'b', 1 }, { 'a', 1 }, set() ],
                [ { 'a', 1.1 }, { 1, None } ]
            ),
            check(
                set(),
                [ { 'a', 'b' }, { 'a' }, set() ],
                [ ]
            ),
        ]

        for check in checks:
            print("Checking %s" % (check.test, ))

            for value in check.good:
                print("\tShould accept %s" % (value, ))

                @typechecked
                def test(a: check.test) -> check.test:
                    return value
                self.assertEqual(value, test(value))

            for value in check.bad + simple_types:
                print("\tShould reject %s" % (value, ))

                @typechecked
                def test(a: check.test):
                    pass
                self.assertRaises(TypeError, test, value)

                @typechecked
                def test(a) -> check.test:
                    return value
                self.assertRaises(TypeError, test, value)

class UnionTest(unittest.TestCase):

    def test_union_is_type(self):
        self.assertIsInstance(union(int, float), type)

    def test_union_with_no_type(self):
        self.assertRaises(TypeError, union, 1, int, 'three')

    def test_isinstance_bultin_types(self):
        self.assertIsInstance(1, union(int, float))
        self.assertIsInstance(1.2, union(int, float))

        self.assertNotIsInstance('string', union(int, float))
        self.assertNotIsInstance([], union(int, float))
        self.assertNotIsInstance(tuple(), union(int, float))
        self.assertNotIsInstance({}, union(int, float))

    def test_isinstance_classes(self):

        class Test1: pass
        class Test2: pass
        class Other: pass

        self.assertIsInstance(Test1(), union(Test1, Test2))
        self.assertIsInstance(Test2(), union(Test1, Test2))

        self.assertNotIsInstance(Other(), union(Test1, Test2))

    def test_isinstance_subclasses(self):

        class Test1: pass
        class Test1Sub(Test1): pass
        class Test2: pass
        class Test2Sub(Test2): pass
        class Other: pass

        self.assertIsInstance(Test1Sub(), union(Test1, Test2))
        self.assertIsInstance(Test2Sub(), union(Test1, Test2))

        self.assertNotIsInstance(Other(), union(Test1, Test2))
        self.assertNotIsInstance(Test1(), union(Test1Sub, Test2Sub))
        self.assertNotIsInstance(Test2(), union(Test1Sub, Test2Sub))

    def test_isinstance_interfaces(self):

        class Test1(Interface):
            def test1() -> int:
                pass
        class Test1Implementation:
            def test1(self) -> int:
                return 1
        class Test2(Interface):
            def test2() -> str:
                pass
        class Test2Implementation:
            def test2(self) -> str:
                return 1
        class Other: pass

        self.assertIsInstance(Test1Implementation(), union(Test1, Test2))
        self.assertIsInstance(Test2Implementation(), union(Test1, Test2))

        self.assertNotIsInstance(Other(), union(Test1, Test2))

    def test_isinstance_mixed(self):

        class Test1:
            pass

        class Test2(Interface):
            def test2() -> str:
                pass

        class Test2Implementation:
            def test2() -> str:
                return 1

        class Other:
            pass

        self.assertIsInstance(1, union(int, Test1, Test2))
        self.assertIsInstance(Test1(), union(int, Test1, Test2))
        self.assertIsInstance(Test2Implementation(), union(int, Test1, Test2))

        self.assertNotIsInstance('string', union(int, Test1, Test2))
        self.assertNotIsInstance(Other(), union(int, Test1, Test2))


    def test_issubclass_single_builtin_type(self):
        self.assertTrue(issubclass(int, union(int, float)))
        self.assertTrue(issubclass(float, union(int, float)))

        self.assertFalse(issubclass(str, union(int, float)))
        self.assertFalse(issubclass(list, union(int, float)))

    def test_issubclass_single_class(self):
        class Test1: pass
        class Test2: pass
        class Other: pass

        self.assertTrue(issubclass(Test1, union(Test1, Test2)))
        self.assertTrue(issubclass(Test2, union(Test1, Test2)))

        self.assertFalse(issubclass(Other, union(Test1, Test2)))

    def test_issubclass_single_subclass(self):
        class Test1: pass
        class Test1Sub(Test1): pass
        class Test2: pass
        class Test2Sub(Test2): pass
        class Other: pass

        self.assertTrue(issubclass(Test1Sub, union(Test1, Test2)))
        self.assertTrue(issubclass(Test2Sub, union(Test1, Test2)))

        self.assertFalse(issubclass(Other, union(Test1, Test2)))
        self.assertFalse(issubclass(Test1, union(Test1Sub, Test2Sub)))
        self.assertFalse(issubclass(Test2, union(Test1Sub, Test2Sub)))

    def test_issubclass_single_interface(self):

        class Test1(Interface):
            def test1(self) -> int:
                pass

        class Test2(Interface):
            def test2(self) -> str:
                pass

        class Other(Interface): pass
        class Other2: pass

        self.assertTrue(issubclass(Test1, union(Test1, Test2)))
        self.assertTrue(issubclass(Test2, union(Test1, Test2)))

        self.assertFalse(issubclass(Other, union(Test1, Test2)))
        self.assertFalse(issubclass(Other2, union(Test1, Test2)))

    def test_issubclass_single_mixed(self):

        class Test1(Interface):
            def test1(self) -> int:
                pass

        class Test2:
            pass

        self.assertTrue(issubclass(int, union(int, Test1, Test2)))
        self.assertTrue(issubclass(Test1, union(int, Test1, Test2)))
        self.assertTrue(issubclass(Test2, union(int, Test1, Test2)))

        self.assertTrue(issubclass(int, union(int, Test1, Test2)))
        self.assertTrue(issubclass(Test1, union(int, Test1, Test2)))
        self.assertTrue(issubclass(Test2, union(int, Test1, Test2)))

    def test_issubclass_union(self):
        self.assertTrue(issubclass(union(int, float), union(int, float)))
        self.assertTrue(issubclass(union(int, float), union(float, int)))
        self.assertTrue(issubclass(union(int, float), union(int, float, bool)))

        self.assertFalse(issubclass(union(int, float), union(int, str)))
        self.assertFalse(issubclass(union(int, str, float), union(int, float)))


class AnyTypeTest(unittest.TestCase):

    def test_isinstance(self):

        class Test:
            pass

        self.assertIsInstance(1, AnyType)
        self.assertIsInstance('string', AnyType)
        self.assertIsInstance(Test(), AnyType)
        self.assertIsInstance(None, AnyType)

    def test_issubclass(self):

        class Test:
            pass

        self.assertTrue(issubclass(int, AnyType))
        self.assertTrue(issubclass(str, AnyType))
        self.assertTrue(issubclass(type, AnyType))
        self.assertTrue(issubclass(Interface, AnyType))


class InterfaceTest(unittest.TestCase):

    def test_matching_arguments_annotations(self):

        class TestInterface(Interface):
            def test(a: int, b: str):
                pass


        class TestImplementation:
            def test(self, a: int, b: str ):
                return 1


        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_arguments_without_annotation(self):

        class TestInterface(Interface):
            def test(a, b):
                pass


        class TestImplementation:
            def test(self, a, b):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_arguments_annotated_in_interface_only(self):

        class TestInterface(Interface):
            def test(a: int, b: str):
                pass


        class TestImplementation:
            def test(self, a, b):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_arguments_with_union_annotations(self):

        class TestInterface(Interface):
            def test(a: union(int, float)) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float)) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_arguments_with_interface(self):

        class TestInterface1(Interface):
            def test1(x, y):
                pass

        class TestInterface2(Interface):
            def test2(a: TestInterface1):
                pass

        class TestImplementation:
            def test2(self, a: TestInterface1):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface2)
        self.assertTrue(issubclass(TestImplementation, TestInterface2))

    def test_arguments_with_annotations_not_matching(self):

        class TestInterface(Interface):
            def test(a: int, b: str) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: int) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_arguments_in_different_order(self):

        class TestInterface(Interface):
            def test(b: str, a: int) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_arguments_with_different_name(self):
        class TestInterface(Interface):
            def test(a: int, b: int) -> int:
                pass


        class TestImplementation:
            def test(self, c: int, d: int) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_arguments_with_different_length(self):

        class TestInterface(Interface):
            def test(a: int) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_arguments_annotated_in_implementation_only(self):

        class TestInterface(Interface):
            def test(a, b) -> int:
                pass

        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_matching_return(self):
        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_without_annotation(self):
        class TestInterface(Interface):
            def test():
                pass


        class TestImplementation:
            def test(self):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_annotated_in_implementation_only(self):
        class TestInterface(Interface):
            def test():
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_with_tuple_annotations(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(int, float):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_with_tuple_annotations_different_order(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(float, int):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_with_subset(self):
        class TestInterface(Interface):
            def test() -> union(int, float, bool):
                pass


        class TestImplementation:
            def test(self) -> union(float, int):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_matching_return_with_single_subset(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)
        self.assertTrue(issubclass(TestImplementation, TestInterface))

    def test_return_with_annotation_not_matching(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> str:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_return_annotated_in_interface_only(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_return_superset(self):

        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(int, float, str):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_return_single_superset(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> union(int, float):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)
        self.assertFalse(issubclass(TestImplementation, TestInterface))

    def test_matching_attribute(self):
        class TestInterface(Interface):
            x = int

        class TestImplementation1:
            def __init__(self):
                self.x = 1

        class TestImplementation2:
            @property
            def x(self):
                return 1

        self.assertIsInstance(TestImplementation1(), TestInterface)
        self.assertIsInstance(TestImplementation2(), TestInterface)

    def test_matching_attribute_with_anytype(self):

        class TestInterface(Interface):
            x = AnyType

        class TestImplementation1:
            def __init__(self):
                self.x = 1

        class TestImplementation2:
            def __init__(self):
                self.x = 'string'

        self.assertIsInstance(TestImplementation1(), TestInterface)
        self.assertIsInstance(TestImplementation2(), TestInterface)

    def test_matching_attribute_with_union(self):

        class TestInterface(Interface):
            x = union(int, str)

        class TestImplementation1:
            def __init__(self):
                self.x = 1

        class TestImplementation2:
            def __init__(self):
                self.x = 'string'

        self.assertIsInstance(TestImplementation1(), TestInterface)
        self.assertIsInstance(TestImplementation2(), TestInterface)

    def test_attribute_with_different_type(self):

        class TestInterface(Interface):
            x = int

        class Other:
            def __init__(self):
                self.x = 'string'


        self.assertNotIsInstance(Other(), TestInterface)

    def test_attribute_not_in_implementation(self):

        class TestInterface(Interface):
            x = AnyType
            y = int

        class Other:
            y = int

        self.assertNotIsInstance(Other(), TestInterface)

    def test_attribute_with_type_not_in_union(self):

        class TestInterface(Interface):
            x = union(int, str)

        class Other:
            x = 1.5

        self.assertNotIsInstance(Other(), TestInterface)

    def test_multiple_attributes(self):

        class TestInterface(Interface):
            x = AnyType
            y = int

        class TestImplementation1:
            def __init__(self):
                self.x = 'hello'
                self.y = 1

        class TestImplementation2:
            x = 'string'

            @property
            def y(self):
                return 1

        self.assertIsInstance(TestImplementation1(), TestInterface)
        self.assertIsInstance(TestImplementation2(), TestInterface)

    def test_multiple_matching_function(self):

        class TestInterface(Interface):
            def test1(a: int) -> int:
                pass

            def test2(b: str) -> str:
                pass

            def test3(c: bool) -> bool:
                pass


        class TestImplementation:
            def test1(self, a: int) -> int:
                return 1

            def test2(self, b: str) -> str:
                return 'string'

            def test3(self, c: bool) -> bool:
                return False

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_implementation_with_extra_functions(self):

        class TestInterface(Interface):
            def test1(a: int) -> int:
                pass

        class TestImplementation:
            def test1(self, a: int) -> int:
                return 1

            def test2(self, b: str) -> str:
                return 'string'

            def test3(self, c: bool) -> bool:
                return False

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_builtin_implementation(self):

        class TestInterface(Interface):
            def __len__():
                pass

        self.assertIsInstance([], TestInterface)
        self.assertIsInstance('', TestInterface)
        self.assertIsInstance(set(), TestInterface)

        self.assertNotIsInstance(iter([]), TestInterface)
        self.assertNotIsInstance(1, TestInterface)

    def test_self_referencing_interface(self):
        class TreeNode(Interface):
            pass

        TreeNode.add_attribute('left', optional(TreeNode))
        TreeNode.add_attribute('right', optional(TreeNode))

        class TreeNodeImplementation:
            def __init__(self):
                self.left = None
                self.right = None

        tree = TreeNodeImplementation()
        tree.left = TreeNodeImplementation()
        tree.right = TreeNodeImplementation()

        self.assertIsInstance(tree, TreeNode)

        tree.left = 1
        self.assertNotIsInstance(tree, TreeNode)

    def test_interface_add_method(self):

        class Test(Interface):
            pass

        @Test.add_method
        def test(x: int) -> int:
            pass

        class TestImplementation:
            def test(self, x: int) -> int:
                return 1

        class Other: pass

        self.assertIsInstance(TestImplementation(), Test)
        self.assertNotIsInstance(Other(), Test)

    def test_interface_add_method_with_no_method(self):

        class Test(Interface):
            pass

        self.assertRaises(TypeError, Test.add_method, 1)

    def test_interface_add_attribute(self):

        class Test(Interface):
            pass

        Test.add_attribute('x', int)

        class TestImplementation:
            x = 1

        class Other: pass

        self.assertIsInstance(TestImplementation(), Test)
        self.assertNotIsInstance(Other(), Test)

    def test_interface_add_attribute_with_no_type(self):

        class Test(Interface):
            pass

        self.assertRaises(TypeError, Test.add_attribute, 'name', 1)

    def test_interface_with_no_type_attribute(self):

        def test():
            class Test(Interface):
                x = 1

        self.assertRaises(TypeError, test)

    def test_interface_complex_list_type(self):

        class TestInterface(Interface):
            def test1(a: [ int ]) -> [ int, str ]:
                pass

        class TestImplementation:
            def test1(self, a: [ int ]) -> [ int, str ]:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

        class TestInterface(Interface):
            def test1(a: [ ]) -> [ ]:
                pass

        class TestImplementation:
            def test1(self, a: [ ]) -> [ ]:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_interface_complex_set_type(self):

        class TestInterface(Interface):
            def test1(a: { int }) -> { int, str }:
                pass

        class TestImplementation:
            def test1(self, a: { int }) -> { int, str }:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

        class TestInterface(Interface):
            def test1(a: set()) -> set():
                pass

        class TestImplementation:
            def test1(self, a: set()) -> set():
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_interface_complex_tuple_type(self):

        class TestInterface(Interface):
            def test1(a: ( str, int )) -> (str, ):
                pass

        class TestImplementation:
            def test1(self, a: ( str, int )) -> (str, ):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

        class TestInterface(Interface):
            def test1(a: tuple()) -> tuple():
                pass

        class TestImplementation:
            def test1(self, a: tuple()) -> tuple():
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_interface_complex_dict_type(self):

        class TestInterface(Interface):
            def test1(a: { int: str, str: int }) -> { }:
                pass

        class TestImplementation:
            def test1(self, a: { int: str, str: int }) -> { }:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

        class TestInterface(Interface):
            def test1(a: {}) -> {}:
                pass

        class TestImplementation:
            def test1(self, a: {}) -> {}:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)


class PredicateTest(unittest.TestCase):

    def test_predicate(self):
        self.assertIsInstance(1, predicate(lambda x: x > 0))
        self.assertNotIsInstance(0, predicate(lambda x: x > 0))
        self.assertNotIsInstance(-1, predicate(lambda x: x > 0))

    def test_predicate_called(self):
        called = False

        @predicate
        def positive(x):
            nonlocal called
            called = True
            return x > 0

        self.assertIsInstance(1, positive)
        self.assertTrue(called)

    def test_optional(self):
        self.assertIsInstance(1, optional(int))
        self.assertIsInstance(None, optional(int))
        self.assertNotIsInstance('string', optional(int))

    def test_typedef(self):
        @typedef
        def callback(a: int) -> int:
            pass

        def f1(a: int) -> int:
            return a

        def f2():
            pass

        self.assertIsInstance(f1, callback)
        self.assertNotIsInstance(f2, callback)

    def test_options(self):
        self.assertIsInstance('open', options('open', 'write'))
        self.assertIsInstance('write', options('open', 'write'))
        self.assertNotIsInstance('other', options('open', 'write'))

    def test_only(self):
        self.assertIsInstance(1, only(int))
        self.assertNotIsInstance(True, only(int))

if __name__ == '__main__':
    unittest.main()
