class GenerationConfig:
    """
    Configuration for content generation parameters and limits.
    """

    def __init__(self, max_content_size: int, allowed_content_types: list):
        self.max_content_size = max_content_size
        self.allowed_content_types = allowed_content_types

    def is_content_type_allowed(self, content_type: str) -> bool:
        """
        Check if the given content type is allowed for generation.
        """
        return content_type in self.allowed_content_types

    def __repr__(self):
        return f"GenerationConfig(max_content_size={self.max_content_size}, allowed_content_types={self.allowed_content_types})"