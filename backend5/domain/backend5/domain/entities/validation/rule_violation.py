class RuleViolation:
    """
    Represents a violation of business rules or validation constraints.
    """

    def __init__(self, rule_name: str, message: str):
        self.rule_name = rule_name  # Name of the violated rule
        self.message = message        # Description of the violation

    def __repr__(self):
        return f"RuleViolation(rule_name={self.rule_name}, message={self.message})"