class GenerationRepository:
    """
    Interface for the Generation Repository.
    Defines methods for managing generation-related entities.
    """

    def add_generation_request(self, request):
        """
        Add a new generation request to the repository.
        """
        raise NotImplementedError

    def get_generation_request(self, request_id):
        """
        Retrieve a generation request by its ID.
        """
        raise NotImplementedError

    def update_generation_result(self, result):
        """
        Update an existing generation result in the repository.
        """
        raise NotImplementedError

    def get_generation_results(self, filter_criteria):
        """
        Retrieve generation results based on specified criteria.
        """
        raise NotImplementedError

    def delete_generation_request(self, request_id):
        """
        Delete a generation request from the repository.
        """
        raise NotImplementedError