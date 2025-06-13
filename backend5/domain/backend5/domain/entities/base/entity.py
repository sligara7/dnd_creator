class Entity:
    """
    Base entity class with an ID.
    """

    def __init__(self, id: str):
        self.id = id

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<Entity id={self.id}>"