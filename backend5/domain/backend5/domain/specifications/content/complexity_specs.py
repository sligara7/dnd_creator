class ComplexitySpecification:
    """
    Specification for evaluating the complexity of D&D content.
    """

    def __init__(self, complexity_level):
        self.complexity_level = complexity_level

    def is_satisfied_by(self, content):
        """
        Check if the content meets the complexity requirements.
        """
        return content.complexity <= self.complexity_level

    def get_violation_reasons(self, content):
        """
        Provide reasons for any complexity violations.
        """
        if content.complexity > self.complexity_level:
            return [f"Content complexity {content.complexity} exceeds the allowed level of {self.complexity_level}."]
        return []