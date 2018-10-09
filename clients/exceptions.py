class ApiResponseError(Exception):
    """Raised when the 3rd-party API has returned an unexpected error"""
    pass


class UnknownProfileError(ApiResponseError):
    """Raised when attempting to retrieve information on a non-existent user"""
    pass


class RateLimitError(ApiResponseError):
    """Raised when the 3rd-party service's rate limit has been hit"""
    pass


class InvalidCredentialsError(ApiResponseError):
    """Raised on failed authentication"""
    pass
