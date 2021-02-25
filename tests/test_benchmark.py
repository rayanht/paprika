import time
import unittest

from paprika import access_counter, data, timeit


class BenchmarkTestCases(unittest.TestCase):
    @data
    class Person:
        age: int
        name: str

    def test_timeit(self):
        def test_handler(_, run_time):
            self.assertAlmostEqual(run_time, 5, delta=0.5)

        @timeit(handler=test_handler)
        def f():
            time.sleep(5)

        f()

    def test_access_counter_mixed_types(self):
        def handler(results):
            self.assertEqual(results["list"]["nWrites"], 100)
            self.assertEqual(results["dict"]["nWrites"], 100)
            self.assertEqual(results["person"]["nWrites"], 100)
            self.assertEqual(results["tuple"]["nWrites"], 0)

            self.assertEqual(results["list"]["nReads"], 0)
            self.assertEqual(results["dict"]["nReads"], 100)
            self.assertEqual(results["person"]["nReads"], 100)
            self.assertEqual(results["tuple"]["nReads"], 100)

        @access_counter(test_mode=True, test_handler=handler)
        def f(list, dict, person, tuple):
            for i in range(100):
                list[0] = dict["key"]
                dict["key"] = person.age
                person.age = tuple[0]

        f([1, 2, 3, 4, 5], {"key": 0}, self.Person(name="Rayan", age=19), (0, 0))

    def test_access_counter_objects(self):
        def handler(results):
            self.assertEqual(results["person1"]["nWrites"], 100)
            self.assertEqual(results["person2"]["nWrites"], 0)

            self.assertEqual(results["person1"]["nReads"], 0)
            self.assertEqual(results["person2"]["nReads"], 100)

        @access_counter(test_mode=True, test_handler=handler)
        def f(person1, person2):
            for i in range(100):
                person1.age = person2.age

        f(self.Person(age=19, name="Rayan"), self.Person(age=91, name="nayaR"))

    def test_access_counter_dicts(self):
        def handler(results):
            self.assertEqual(results["dict1"]["nWrites"], 100)
            self.assertEqual(results["dict2"]["nWrites"], 0)

            self.assertEqual(results["dict1"]["nReads"], 0)
            self.assertEqual(results["dict2"]["nReads"], 100)

        @access_counter(test_mode=True, test_handler=handler)
        def f(dict1, dict2):
            for i in range(100):
                dict1[0] = dict2[0]

        f({0: 1}, {0: 1})

    def test_access_counter_lists(self):
        def handler(results):
            self.assertEqual(results["list1"]["nWrites"], 100)
            self.assertEqual(results["list2"]["nWrites"], 0)

            self.assertEqual(results["list1"]["nReads"], 0)
            self.assertEqual(results["list2"]["nReads"], 100)

        @access_counter(test_mode=True, test_handler=handler)
        def f(list1, list2):
            for i in range(100):
                list1[0] = list2[0]

        f([0], [0])
