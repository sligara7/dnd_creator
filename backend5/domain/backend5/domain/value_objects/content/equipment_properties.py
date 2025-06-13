class EquipmentProperties:
    """
    Represents the properties of equipment in the D&D content framework.
    """

    def __init__(self, weight: float, cost: float, properties: list):
        self.weight = weight  # Weight of the equipment
        self.cost = cost      # Cost of the equipment
        self.properties = properties  # List of properties (e.g., 'magical', 'heavy')

    def __repr__(self):
        return f"EquipmentProperties(weight={self.weight}, cost={self.cost}, properties={self.properties})"

    def to_dict(self):
        """
        Converts the EquipmentProperties instance to a dictionary.
        """
        return {
            "weight": self.weight,
            "cost": self.cost,
            "properties": self.properties
        }