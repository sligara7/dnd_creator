class Background:
    """
    Represents a character's background in the D&D framework.
    Contains information about the character's history, traits, and motivations.
    """

    def __init__(self, name: str, description: str, features: list):
        self.name = name  # Name of the background
        self.description = description  # Description of the background
        self.features = features  # List of features associated with the background

    def __repr__(self):
        return f"Background(name={self.name}, description={self.description}, features={self.features})"

    def add_feature(self, feature: str):
        """
        Adds a feature to the background.
        """
        self.features.append(feature)

    def remove_feature(self, feature: str):
        """
        Removes a feature from the background if it exists.
        """
        if feature in self.features:
            self.features.remove(feature)