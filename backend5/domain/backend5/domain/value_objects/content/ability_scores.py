class AbilityScores:
    """
    Represents a collection of ability scores for a character in D&D.
    Ability scores typically include Strength, Dexterity, Constitution,
    Intelligence, Wisdom, and Charisma.
    """

    def __init__(self, strength: int, dexterity: int, constitution: int,
                 intelligence: int, wisdom: int, charisma: int):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    def total(self) -> int:
        """
        Calculate the total of all ability scores.
        """
        return (self.strength + self.dexterity + self.constitution +
                self.intelligence + self.wisdom + self.charisma)

    def __repr__(self) -> str:
        return (f"AbilityScores(strength={self.strength}, "
                f"dexterity={self.dexterity}, constitution={self.constitution}, "
                f"intelligence={self.intelligence}, wisdom={self.wisdom}, "
                f"charisma={self.charisma})")

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbilityScores):
            return NotImplemented
        return (self.strength == other.strength and
                self.dexterity == other.dexterity and
                self.constitution == other.constitution and
                self.intelligence == other.intelligence and
                self.wisdom == other.wisdom and
                self.charisma == other.charisma)