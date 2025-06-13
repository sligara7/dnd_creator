class Template:
    """
    Represents a template entity used for content generation.
    """

    def __init__(self, id: str, name: str, description: str, content_type: str):
        self.id = id  # Unique identifier for the template
        self.name = name  # Name of the template
        self.description = description  # Description of the template
        self.content_type = content_type  # Type of content this template generates

    def __repr__(self):
        return f"Template(id={self.id}, name={self.name}, content_type={self.content_type})"

    def to_dict(self):
        """
        Converts the template instance to a dictionary representation.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type,
        }