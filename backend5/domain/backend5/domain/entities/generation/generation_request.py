class GenerationRequest:
    """
    Represents a request for content generation, encapsulating the necessary parameters
    and context for generating D&D content based on user input and specifications.
    """

    def __init__(self, concept: str, target_level: int, content_types: list):
        self.concept = concept  # The character concept or background
        self.target_level = target_level  # The desired level for the generated content
        self.content_types = content_types  # List of content types to generate (e.g., spells, feats)

    def validate(self):
        """
        Validates the generation request parameters.
        Raises exceptions if any validation rules are violated.
        """
        if not isinstance(self.concept, str) or not self.concept:
            raise ValueError("Concept must be a non-empty string.")
        if not isinstance(self.target_level, int) or self.target_level <= 0:
            raise ValueError("Target level must be a positive integer.")
        if not isinstance(self.content_types, list) or not self.content_types:
            raise ValueError("Content types must be a non-empty list.")

    def to_dict(self):
        """
        Converts the generation request to a dictionary representation.
        This can be useful for serialization or logging purposes.
        """
        return {
            "concept": self.concept,
            "target_level": self.target_level,
            "content_types": self.content_types
        }