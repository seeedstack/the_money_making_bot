# platforms/twitter/errors.py

class TwitterError(Exception):
    """Base Twitter error."""
    pass

class LoginError(TwitterError):
    """Login failed."""
    pass

class APIError(TwitterError):
    """Tweepy API call failed."""
    pass

class NetworkError(TwitterError):
    """Network/connection error."""
    pass
