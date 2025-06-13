class BalanceSpecification:
    """
    Encapsulates D&D 5e balance requirements
    as executable specifications.
    """

    def __init__(self, min_power_level: int, max_power_level: int):
        self.min_power_level = min_power_level
        self.max_power_level = max_power_level

    def is_satisfied_by(self, content) -> bool:
        """
        Check if the content satisfies the balance requirements.
        """
        return self.min_power_level <= content.power_level <= self.max_power_level

    def get_violation_reasons(self, content) -> list:
        """
        Get reasons for violation of balance specifications.
        """
        reasons = []
        if content.power_level < self.min_power_level:
            reasons.append(f"Power level {content.power_level} is below the minimum required {self.min_power_level}.")
        if content.power_level > self.max_power_level:
            reasons.append(f"Power level {content.power_level} exceeds the maximum allowed {self.max_power_level}.")
        return reasons