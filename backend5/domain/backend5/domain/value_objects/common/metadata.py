class Metadata:
    """
    Represents metadata associated with content in the D&D framework.
    This includes information such as title, description, author, and creation date.
    """

    def __init__(self, title: str, description: str, author: str, creation_date: str):
        self.title = title
        self.description = description
        self.author = author
        self.creation_date = creation_date

    def to_dict(self) -> dict:
        """
        Converts the metadata to a dictionary representation.
        """
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "creation_date": self.creation_date,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a Metadata instance from a dictionary.
        """
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            author=data.get("author"),
            creation_date=data.get("creation_date"),
        )