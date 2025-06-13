class BalanceAssessedEvent:
    """
    Event published when a balance assessment is completed.
    Contains details about the assessed content and the results.
    """

    def __init__(self, content_id: str, assessment_result: dict):
        self.content_id = content_id
        self.assessment_result = assessment_result

    def get_content_id(self) -> str:
        return self.content_id

    def get_assessment_result(self) -> dict:
        return self.assessment_result

    def __repr__(self) -> str:
        return f"<BalanceAssessedEvent content_id={self.content_id} assessment_result={self.assessment_result}>"