class GenerationRequestedEvent:
    """
    Event published when a generation request is made.
    Contains details about the request for further processing.
    """

    def __init__(self, request_id: str, user_id: str, content_type: str, parameters: dict):
        self.request_id = request_id  # Unique identifier for the generation request
        self.user_id = user_id          # Identifier for the user making the request
        self.content_type = content_type  # Type of content being requested (e.g., spell, character)
        self.parameters = parameters      # Additional parameters for the generation process

    def __repr__(self):
        return f"<GenerationRequestedEvent(request_id={self.request_id}, user_id={self.user_id}, content_type={self.content_type})>"