import time
import unittest

from paprika import sleep_after, sleep_before, repeat


class UtilityTestCases(unittest.TestCase):
    # We cannot be too sure that sleeping exceeds the time, so give it 10ms leeway
    SLEEP_TOLERANCE = 0.01

    def test_sleep_after(self):
        start = time.perf_counter()

        @sleep_after(duration=2)
        def f():
            self.assertLess(time.perf_counter() - start, 0.5)

        f()
        self.assertGreaterEqual(time.perf_counter() - start, 2.0 - self.SLEEP_TOLERANCE)

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
