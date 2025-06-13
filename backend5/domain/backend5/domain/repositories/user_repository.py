class UserRepository:
    """
    Interface for user repository operations.
    """

    def get_user_by_id(self, user_id: str) -> User:
        """
        Retrieve a user by their unique identifier.

        :param user_id: The unique identifier of the user.
        :return: The user entity.
        """
        pass

    def create_user(self, user: User) -> None:
        """
        Create a new user in the repository.

        :param user: The user entity to be created.
        """
        pass

    def update_user(self, user: User) -> None:
        """
        Update an existing user in the repository.

        :param user: The user entity with updated information.
        """
        pass

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user from the repository.

        :param user_id: The unique identifier of the user to be deleted.
        """
        pass

    def get_all_users(self) -> List[User]:
        """
        Retrieve all users from the repository.

        :return: A list of user entities.
        """
        pass