class Equipment:
    def __init__(self, name: str, description: str, weight: float, properties: dict):
        self.name = name
        self.description = description
        self.weight = weight
        self.properties = properties

    def __repr__(self):
        return f"<Equipment(name={self.name}, weight={self.weight})>"

    def get_details(self):
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "properties": self.properties
        }