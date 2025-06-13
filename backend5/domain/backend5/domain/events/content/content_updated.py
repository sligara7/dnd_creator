class ContentUpdatedEvent:
    """
    Event published when content is updated.
    Contains details about the updated content.
    """

    def __init__(self, content_id: str, updated_fields: dict):
        self.content_id = content_id
        self.updated_fields = updated_fields

    def get_content_id(self) -> str:
        return self.content_id

    def get_updated_fields(self) -> dict:
        return self.updated_fields

    def __repr__(self):
        return f"<ContentUpdatedEvent content_id={self.content_id} updated_fields={self.updated_fields}>"