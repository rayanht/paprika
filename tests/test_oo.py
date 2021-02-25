import unittest

from paprika import data, NonNull, singleton


class OOTestCases(unittest.TestCase):
    @data
    class TestClass:
        field1: NonNull[int]
        field2: str

    @singleton
    class TestSingleton:
        field1: str

    def test_nonnull(self):
        self.assertRaises(
            ValueError, self.TestClass, None, {"field1": None, "field2": "test"}
        )

    def test_to_string(self):
        self.assertEqual(
            str(self.TestClass(field1=42, field2="test")),
            "TestClass@[field1=42, field2=test]",
        )

    def test_eq(self):
        t1 = self.TestClass(field1=42, field2="test")
        t2 = self.TestClass(field1=42, field2="test")
        self.assertEqual(t1, t2)

    def test_hash(self):
        t1 = self.TestClass(field1=42, field2="test")
        t2 = self.TestClass(field1=42, field2="test")
        self.assertEqual(hash(t1), hash(t2))

    def test_singleton(self):
        s1 = self.TestSingleton(field1="test")
        s2 = self.TestSingleton()
        self.assertEqual(s1, s2)
