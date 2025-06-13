class Subclass:
    """
    Represents a subclass in the D&D character system.
    This class encapsulates the properties and behaviors specific to a subclass.
    """

    def __init__(self, name: str, description: str, features: list):
        self.name = name  # Name of the subclass
        self.description = description  # Description of the subclass
        self.features = features  # List of features associated with the subclass

    def get_details(self):
        """
        Returns the details of the subclass including name, description, and features.
        """
        return {
            "name": self.name,
            "description": self.description,
            "features": self.features
        }