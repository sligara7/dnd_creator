class BaseRepository:
    """
    Base repository interface for domain entities.
    Defines common methods for data access and manipulation.
    """

    def add(self, entity):
        """
        Add a new entity to the repository.
        """
        raise NotImplementedError("Method not implemented.")

    def get(self, entity_id):
        """
        Retrieve an entity by its ID.
        """
        raise NotImplementedError("Method not implemented.")

    def update(self, entity):
        """
        Update an existing entity in the repository.
        """
        raise NotImplementedError("Method not implemented.")

    def delete(self, entity_id):
        """
        Delete an entity from the repository by its ID.
        """
        raise NotImplementedError("Method not implemented.")

    def list(self):
        """
        List all entities in the repository.
        """
        raise NotImplementedError("Method not implemented.")