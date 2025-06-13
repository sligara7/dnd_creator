class GenerationResult:
    """
    Represents the result of a content generation process.
    Contains the generated content and associated metadata.
    """

    def __init__(self, content, success: bool, errors=None):
        self.content = content  # The generated content
        self.success = success  # Indicates if the generation was successful
        self.errors = errors or []  # List of errors encountered during generation

    def add_error(self, error: str):
        """
        Adds an error message to the result.
        """
        self.errors.append(error)

    def __repr__(self):
        return f"<GenerationResult(success={self.success}, content={self.content}, errors={self.errors})>"