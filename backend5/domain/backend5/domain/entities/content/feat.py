class Feat:
    """
    Represents a feat in the D&D system, which provides characters with special abilities or enhancements.
    """

    def __init__(self, name: str, description: str, prerequisites: list = None):
        self.name = name
        self.description = description
        self.prerequisites = prerequisites if prerequisites is not None else []

    def __repr__(self):
        return f"Feat(name={self.name}, description={self.description}, prerequisites={self.prerequisites})"

    def is_available(self, character) -> bool:
        """
        Check if the feat is available for the given character based on prerequisites.
        """
        return all(prerequisite in character.feats for prerequisite in self.prerequisites)