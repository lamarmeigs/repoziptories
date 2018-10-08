class UnknownProfileError(Exception):
    """Raised when attempting to retrieve information on a non-existent user"""
    pass


class RateLimitError(Exception):
    """Raised when the 3rd-party service's rate limit has been hit"""
    pass
