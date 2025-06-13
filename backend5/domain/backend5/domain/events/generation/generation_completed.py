class GenerationCompletedEvent:
    """
    Event published when a generation process is completed.
    Contains details about the generated content and any relevant metadata.
    """

    def __init__(self, generation_id: str, content_id: str, success: bool, message: str = ""):
        self.generation_id = generation_id  # Unique identifier for the generation process
        self.content_id = content_id          # Unique identifier for the generated content
        self.success = success                # Indicates if the generation was successful
        self.message = message                # Optional message providing additional context

    def __repr__(self):
        return (f"<GenerationCompletedEvent(generation_id={self.generation_id}, "
                f"content_id={self.content_id}, success={self.success}, "
                f"message='{self.message}')>")