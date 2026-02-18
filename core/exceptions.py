class BackoffError(Exception):
    """Raised when the server is requesting a backoff (e.g. 503)."""
    pass

class DataIntegrityError(Exception):
    """Raised when downloaded data fails validation."""
    pass
