import unittest

from paprika import catch, silent_catch


class ErrorHandlingTestCases(unittest.TestCase):
    def test_catch_catches(self):
        @catch(exception=BlockingIOError)
        def f():
            raise BlockingIOError

        f()
        self.assertTrue(True)

    def test_catch_doesnt_catch_unspecified(self):
        @catch(exception=BlockingIOError)
        def f():
            raise ValueError

        self.assertRaises(ValueError, f)

    def test_catch_uses_handler(self):
        def switcheroo_handler(e):
            raise ConnectionError from e

        @catch(exception=ValueError, handler=switcheroo_handler)
        def f():
            raise ValueError

        self.assertRaises(ConnectionError, f)

    def test_silent_catch_catches(self):
        @silent_catch(exception=BlockingIOError)
        def f():
            raise BlockingIOError

        f()
        self.assertTrue(True)

    def test_catch_catches_multiple(self):
        @catch(exception=[FileExistsError, IndexError, IndentationError])
        def f():
            raise IndexError

        f()
        self.assertTrue(True)

    def test_silent_catch_catches_multiple(self):
        @catch(exception=[FileExistsError, IndexError, IndentationError])
        def f():
            raise IndentationError

        f()
        self.assertTrue(True)
