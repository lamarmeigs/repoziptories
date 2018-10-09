from unittest import TestCase

from clients import exceptions


class ApiResponseErrorTestcase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(exceptions.ApiResponseError(), Exception)


class UnknownProfileErrorTestCase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(
            exceptions.UnknownProfileError(),
            exceptions.ApiResponseError
        )


class RateLimitErrorTestCase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(
            exceptions.RateLimitError(),
            exceptions.ApiResponseError
        )


class InvalidCredentialsErrorTestCase(TestCase):
    def test_inheritance(self):
        self.assertIsInstance(
            exceptions.InvalidCredentialsError(),
            exceptions.ApiResponseError
        )
