class ValidationAggregate:
    """
    Validation aggregate managing the lifecycle of validation processes,
    including validation results and rule violations.
    """
    
    def __init__(self):
        self.validation_results = []
        self.rule_violations = []

    def add_validation_result(self, result):
        self.validation_results.append(result)

    def add_rule_violation(self, violation):
        self.rule_violations.append(violation)

    def clear_validation_results(self):
        self.validation_results.clear()

    def clear_rule_violations(self):
        self.rule_violations.clear()

    def get_validation_summary(self):
        return {
            "results": self.validation_results,
            "violations": self.rule_violations
        }