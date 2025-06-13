class GenerationFailedEvent:
    """
    Event published when a generation process fails.
    Contains details about the failure for logging and analysis.
    """

    def __init__(self, request_id: str, error_message: str):
        self.request_id = request_id  # Unique identifier for the generation request
        self.error_message = error_message  # Description of the failure

    def __repr__(self):
        return f"<GenerationFailedEvent(request_id={self.request_id}, error_message={self.error_message})>"