class ValidationFactory:
    """
    Factory class for creating validation entities.
    """

    @staticmethod
    def create_validation_result(success: bool, messages: list) -> 'ValidationResult':
        """
        Creates a ValidationResult entity.

        :param success: Indicates if the validation was successful.
        :param messages: List of validation messages.
        :return: An instance of ValidationResult.
        """
        return ValidationResult(success=success, messages=messages)

    @staticmethod
    def create_rule_violation(rule_name: str, description: str) -> 'RuleViolation':
        """
        Creates a RuleViolation entity.

        :param rule_name: The name of the violated rule.
        :param description: Description of the violation.
        :return: An instance of RuleViolation.
        """
        return RuleViolation(rule_name=rule_name, description=description)

    @staticmethod
    def create_balance_assessment(content_id: str, score: float, is_balanced: bool) -> 'BalanceAssessment':
        """
        Creates a BalanceAssessment entity.

        :param content_id: The ID of the content being assessed.
        :param score: The balance score.
        :param is_balanced: Indicates if the content is balanced.
        :return: An instance of BalanceAssessment.
        """
        return BalanceAssessment(content_id=content_id, score=score, is_balanced=is_balanced)