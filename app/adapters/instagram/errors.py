# platforms/instagram/errors.py

class InstagramError(Exception):
    """Base Instagram error."""
    pass

class LoginError(InstagramError):
    """Login failed."""
    pass

class APIError(InstagramError):
    """Instagrapi API call failed."""
    pass

class NetworkError(InstagramError):
    """Network/connection error."""
    pass
