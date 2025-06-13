class Prompt:
    """
    Represents a prompt entity used in content generation.
    """

    def __init__(self, id: str, content: str, context: str):
        self.id = id  # Unique identifier for the prompt
        self.content = content  # The prompt content
        self.context = context  # Contextual information for the prompt

    def __repr__(self):
        return f"Prompt(id={self.id}, content={self.content}, context={self.context})"

    def to_dict(self):
        """
        Converts the prompt to a dictionary representation.
        """
        return {
            "id": self.id,
            "content": self.content,
            "context": self.context
        }