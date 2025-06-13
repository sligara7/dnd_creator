class Species:
    """
    Represents a species in the D&D universe with its associated attributes and behaviors.
    """

    def __init__(self, name: str, traits: list, speed: int):
        self.name = name  # Name of the species
        self.traits = traits  # List of traits associated with the species
        self.speed = speed  # Speed of the species in feet

    def get_description(self) -> str:
        """
        Returns a description of the species.
        """
        return f"{self.name} has a speed of {self.speed} feet and possesses the following traits: {', '.join(self.traits)}."

    def add_trait(self, trait: str):
        """
        Adds a new trait to the species.
        """
        self.traits.append(trait)

    def remove_trait(self, trait: str):
        """
        Removes a trait from the species if it exists.
        """
        if trait in self.traits:
            self.traits.remove(trait)