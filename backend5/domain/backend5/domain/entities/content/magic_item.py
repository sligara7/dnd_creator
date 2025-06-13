class MagicItem:
    """
    Represents a magic item in the D&D universe.
    """

    def __init__(self, name: str, description: str, rarity: str, properties: dict):
        self.name = name
        self.description = description
        self.rarity = rarity
        self.properties = properties

    def __repr__(self):
        return f"<MagicItem(name={self.name}, rarity={self.rarity})>"

    def use(self):
        """
        Logic for using the magic item.
        """
        pass

    def get_details(self):
        """
        Returns the details of the magic item.
        """
        return {
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "properties": self.properties,
        }