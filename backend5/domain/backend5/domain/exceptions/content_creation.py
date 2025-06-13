class ContentCreationException(Exception):
    """Base class for exceptions related to content creation."""
    pass

class ContentAlreadyExistsException(ContentCreationException):
    """Exception raised when attempting to create content that already exists."""
    def __init__(self, content_name):
        super().__init__(f"Content '{content_name}' already exists.")

class ContentCreationFailedException(ContentCreationException):
    """Exception raised when content creation fails due to an unknown error."""
    def __init__(self, message):
        super().__init__(f"Content creation failed: {message}")

class InvalidContentDataException(ContentCreationException):
    """Exception raised when the provided content data is invalid."""
    def __init__(self, errors):
        super().__init__(f"Invalid content data: {errors}")