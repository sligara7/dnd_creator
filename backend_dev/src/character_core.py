class CharacterCore:
    def __init__(self):
        # Basic character information
        self.name = ""
        self.species = ""
        self.background = ""
        self.alignment = ""

        # Class information
        self.character_classes = []

        # Personality aspects
        self.personality_traits = []
        self.ideals = []
        self.bonds = []
        self.flaws = []

        # Backstory
        self.backstory = ""
        self.detailed_backstory = ""

        # Ability scores
        self.ability_scores = {
            'strength': 0,
            'dexterity': 0,
            'constitution': 0,
            'intelligence': 0,
            'wisdom': 0,
            'charisma': 0
        }

    # Basic Character Information Setters
    def set_name(self, name: str) -> None:
        """Set the character's name."""
        self.name = name

    def set_species(self, species: str) -> None:
        """Set the character's species."""
        self.species = species

    def set_background(self, background: str) -> None:
        """Set the character's background."""
        self.background = background

    def set_alignment(self, alignment: str) -> None:
        """Set the character's alignment."""
        self.alignment = alignment

    # Class Management Setters
    def set_character_classes(self, character_classes: List[Dict]) -> None:
        """Set the character's classes (for multiclassing updates)."""
        self.character_classes = character_classes

    # Personality Setters
    def set_personality_traits(self, traits: List[str]) -> None:
        """Set the character's personality traits."""
        self.personality_traits = traits

    def set_ideals(self, ideals: List[str]) -> None:
        """Set the character's ideals."""
        self.ideals = ideals

    def set_bonds(self, bonds: List[str]) -> None:
        """Set the character's bonds."""
        self.bonds = bonds

    def set_flaws(self, flaws: List[str]) -> None:
        """Set the character's flaws."""
        self.flaws = flaws

    # Backstory Setters
    def set_backstory(self, backstory: str) -> None:
        """Set the character's backstory."""
        self.backstory = backstory

    def set_detailed_backstory(self, detailed_backstory: str) -> None:
        """Set the character's detailed backstory."""
        self.detailed_backstory = detailed_backstory

    # Individual Ability Score Setters
    def set_strength(self, strength: int) -> None:
        """Set the character's strength score."""
        self.ability_scores['strength'] = strength

    def set_dexterity(self, dexterity: int) -> None:
        """Set the character's dexterity score."""
        self.ability_scores['dexterity'] = dexterity

    def set_constitution(self, constitution: int) -> None:
        """Set the character's constitution score."""
        self.ability_scores['constitution'] = constitution

    def set_intelligence(self, intelligence: int) -> None:
        """Set the character's intelligence score."""
        self.ability_scores['intelligence'] = intelligence

    def set_wisdom(self, wisdom: int) -> None:
        """Set the character's wisdom score."""
        self.ability_scores['wisdom'] = wisdom

    def set_charisma(self, charisma: int) -> None:
        """Set the character's charisma score."""
        self.ability_scores['charisma'] = charisma