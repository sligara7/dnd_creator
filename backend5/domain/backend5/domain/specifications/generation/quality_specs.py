class QualitySpecification:
    """
    Encapsulates quality requirements for generated content.
    """

    def __init__(self, minimum_quality: int, maximum_quality: int):
        self.minimum_quality = minimum_quality
        self.maximum_quality = maximum_quality

    def is_satisfied_by(self, content_quality: int) -> bool:
        """
        Checks if the content quality meets the specified quality requirements.
        """
        return self.minimum_quality <= content_quality <= self.maximum_quality

    def get_violation_reasons(self, content_quality: int) -> list:
        """
        Returns a list of reasons if the content quality does not meet the requirements.
        """
        reasons = []
        if content_quality < self.minimum_quality:
            reasons.append(f"Content quality {content_quality} is below the minimum required quality of {self.minimum_quality}.")
        if content_quality > self.maximum_quality:
            reasons.append(f"Content quality {content_quality} exceeds the maximum allowed quality of {self.maximum_quality}.")
        return reasons