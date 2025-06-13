class ContentValidatedEvent:
    """
    Event published when content has been validated successfully.
    Contains details about the validated content.
    """

    def __init__(self, content_id: str, validation_result: dict):
        self.content_id = content_id
        self.validation_result = validation_result

    def get_content_id(self) -> str:
        return self.content_id

    def get_validation_result(self) -> dict:
        return self.validation_result

    def __repr__(self):
        return f"<ContentValidatedEvent(content_id={self.content_id}, validation_result={self.validation_result})>"