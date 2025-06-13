class DamageResistance:
    """
    Represents the damage resistance characteristics of a character or entity.
    """

    def __init__(self, damage_type: str, resistance_value: int):
        self.damage_type = damage_type
        self.resistance_value = resistance_value

    def __repr__(self):
        return f"DamageResistance(damage_type={self.damage_type}, resistance_value={self.resistance_value})"

    def is_resistant_to(self, damage_type: str) -> bool:
        """
        Check if the entity is resistant to a specific type of damage.
        """
        return self.damage_type.lower() == damage_type.lower()

    def get_resistance_value(self) -> int:
        """
        Get the resistance value for the damage type.
        """
        return self.resistance_value

    def __eq__(self, other):
        if not isinstance(other, DamageResistance):
            return NotImplemented
        return (self.damage_type == other.damage_type and
                self.resistance_value == other.resistance_value)

    def __hash__(self):
        return hash((self.damage_type, self.resistance_value))