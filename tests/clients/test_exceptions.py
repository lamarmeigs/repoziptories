from unittest import TestCase

from clients import exceptions


class UnknownProfileErrorTestCase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(exceptions.UnknownProfileError(), Exception)


class RateLimitErrorTestCase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(exceptions.RateLimitError(), Exception)
