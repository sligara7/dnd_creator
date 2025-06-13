class BalanceAssessment:
    """
    Represents the balance assessment of generated content in the D&D framework.
    This entity encapsulates the metrics and results of balance evaluations.
    """

    def __init__(self, content_id: str, balance_score: float, issues: list):
        self.content_id = content_id  # Unique identifier for the content being assessed
        self.balance_score = balance_score  # Score indicating the balance of the content
        self.issues = issues  # List of identified balance issues

    def is_balanced(self) -> bool:
        """
        Determines if the content is balanced based on the balance score.
        """
        return self.balance_score >= 0  # Assuming a score of 0 or higher indicates balance

    def add_issue(self, issue: str):
        """
        Adds a balance issue to the assessment.
        """
        self.issues.append(issue)

    def __repr__(self):
        return f"<BalanceAssessment(content_id={self.content_id}, balance_score={self.balance_score}, issues={self.issues})>"