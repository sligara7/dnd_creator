class ContentCreatedEvent:
    """
    Event published when new content is created.
    This event triggers validation and analysis workflows.
    """

    def __init__(self, content_id: str, creator_id: str, timestamp: str):
        self.content_id = content_id  # Unique identifier for the created content
        self.creator_id = creator_id    # Identifier for the user who created the content
        self.timestamp = timestamp        # Time when the content was created

    def __repr__(self):
        return f"<ContentCreatedEvent(content_id={self.content_id}, creator_id={self.creator_id}, timestamp={self.timestamp})>"