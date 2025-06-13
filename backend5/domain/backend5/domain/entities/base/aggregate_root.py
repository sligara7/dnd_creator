class AggregateRoot:
    """
    Base class for aggregate roots in the domain model.
    An aggregate root is an entity that serves as the entry point for a cluster of related entities.
    """

    def __init__(self, id):
        self._id = id
        self._is_active = True

    @property
    def id(self):
        return self._id

    @property
    def is_active(self):
        return self._is_active

    def deactivate(self):
        """Deactivate the aggregate root."""
        self._is_active = False

    def activate(self):
        """Activate the aggregate root."""
        self._is_active = True

    def __eq__(self, other):
        if not isinstance(other, AggregateRoot):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)