import unittest
from annotations import typechecked, Interface, union, AnyType


class TypecheckedTest(unittest.TestCase):

    def test_single_argument_with_builtin_type(self):

        @typechecked
        def test(a: int):
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, 'string')
        self.assertRaises(TypeError, test, 1.2)
        self.assertRaises(TypeError, test, None)

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

        class MyClass:
            pass

        class MySubClass(MyClass):
            pass

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
        self.assertRaises(TypeError, test, None, None)

    def test_multiple_arguments_some_with_annotations(self):

        @typechecked
        def test(a, b: str):
            return a, b

        self.assertEqual((1, 'string'), test(1, 'string'))
        self.assertEqual(('string', 'string'), test('string', 'string'))
        self.assertRaises(TypeError, test, 1, 1)
        self.assertRaises(TypeError, test, 'string', 1)
        self.assertRaises(TypeError, test, None, None)

    def test_single_return_annotation(self):

        @typechecked
        def test(a) -> int:
            return a

        self.assertEqual(1, test(1))
        self.assertRaises(TypeError, test, 'string')
        self.assertRaises(TypeError, test, 1.2)
        self.assertRaises(TypeError, test, None)

    def test_union_return_annotations(self):

        @typechecked
        def test(a) -> union(int, float):
            return a

        self.assertEqual(1, test(1))
        self.assertEqual(1.1, test(1.1))
        self.assertRaises(TypeError, test, 'string')
        self.assertRaises(TypeError, test, None)


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
            def test1(self) -> int:
                pass
        class Test1Implementation:
            def test1(self) -> int:
                return 1
        class Test2(Interface):
            def test2(self) -> str:
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
            def test2(self) -> str:
                pass

        class Test2Implementation:
            def test2(self) -> str:
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

    def test_issubclass(self):

        class Test:
            pass

        self.assertTrue(issubclass(int, AnyType))
        self.assertTrue(issubclass(str, AnyType))
        self.assertTrue(issubclass(type, AnyType))
        self.assertTrue(issubclass(Interface, AnyType))


class InterfaceTest(unittest.TestCase):

    def test_matching_arguments(self):

        class TestInterface(Interface):
            def test(a: int, b: str) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str ) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_without_annotation(self):

        class TestInterface(Interface):
            def test(a, b) -> int:
                pass


        class TestImplementation:
            def test(self, a, b) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_annotated_in_interface_only(self):

        class TestInterface(Interface):
            def test(a: int, b: str) -> int:
                pass


        class TestImplementation:
            def test(self, a, b) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_with_union_annotations(self):

        class TestInterface(Interface):
            def test(a: union(int, float)) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float)) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_union_annotations_different_order(self):

        class TestInterface(Interface):
            def test(a: union(float, int)) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float)) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_superset(self):

        class TestInterface(Interface):
            def test(a: union(int, float)) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float, bool)) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_arguments_superset_single_element(self):

        class TestInterface(Interface):
            def test(a: int) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float)) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_arguments_with_annotations_not_matching(self):

        class TestInterface(Interface):
            def test(a: int, b: str) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: int) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_in_different_order(self):

        class TestInterface(Interface):
            def test(b: str, a: int) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_with_different_name(self):
        class TestInterface(Interface):
            def test(a: int, b: int) -> int:
                pass


        class TestImplementation:
            def test(self, c: int, d: int) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_with_different_length(self):

        class TestInterface(Interface):
            def test(a: int) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_annotated_in_implementation_only(self):

        class TestInterface(Interface):
            def test(a, b) -> int:
                pass


        class TestImplementation:
            def test(self, a: int, b: str) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_implement_subset(self):

        class TestInterface(Interface):
            def test(a: union(int, float, str)) -> int:
                pass


        class TestImplementation:
            def test(self, a: union(int, float)) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_arguments_implement_single_subset(self):

        class TestInterface(Interface):
            def test(a: union(int, float)) -> int:
                pass


        class TestImplementation:
            def test(self, a: int) -> int:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_matching_return(self):
        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_without_annotation(self):
        class TestInterface(Interface):
            def test():
                pass


        class TestImplementation:
            def test(self):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_annotated_in_implementation_only(self):
        class TestInterface(Interface):
            def test():
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_with_tuple_annotations(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(int, float):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_with_tuple_annotations_different_order(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(float, int):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_with_subset(self):
        class TestInterface(Interface):
            def test() -> union(int, float, bool):
                pass


        class TestImplementation:
            def test(self) -> union(float, int):
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_matching_return_with_single_subset(self):
        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> int:
                return 1

        self.assertIsInstance(TestImplementation(), TestInterface)

    def test_return_with_annotation_not_matching(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> str:
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_return_annotated_in_interface_only(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_return_superset(self):

        class TestInterface(Interface):
            def test() -> union(int, float):
                pass


        class TestImplementation:
            def test(self) -> union(int, float, str):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

    def test_return_single_superset(self):

        class TestInterface(Interface):
            def test() -> int:
                pass


        class TestImplementation:
            def test(self) -> union(int, float):
                return 1

        self.assertNotIsInstance(TestImplementation(), TestInterface)

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

    @unittest.skip
    def test_self_referencing_interface(self):
        class TestInterface(Interface):
            def test(a: TestInterface) -> TestInterface:
                pass


        class TestImplementation:
            def test(self, a: TestInterface) -> TestInterface:
                return TestImplementation()

        self.assertIsInstance(TestImplementation(), TestInterface)


    def test_sandbox(self):

        class TestInterface(Interface):
            def __iter__():
                pass

        self.assertIsInstance([], TestInterface)


if __name__ == '__main__':
    unittest.main()
