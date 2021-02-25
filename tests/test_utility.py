import time
import unittest

from paprika import access_counter, data, timeit, sleep_after, sleep_before, \
    repeat


class UtilityTestCases(unittest.TestCase):
    def test_sleep_after(self):
        start = time.perf_counter()

        @sleep_after(duration=2)
        def f():
            self.assertLess(time.perf_counter() - start, 0.5)

        f()
        self.assertGreaterEqual(time.perf_counter() - start, 2)

    def test_sleep_before(self):
        start = time.perf_counter()

        @sleep_before(duration=2)
        def f():
            self.assertGreaterEqual(time.perf_counter() - start, 1.5)

        f()

    def test_repeat(self):
        cnt = [0]

        @repeat(n=5)
        def f(counter):
            counter[0] += 1

        f(cnt)

        self.assertEqual(cnt, [5])
