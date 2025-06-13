from typing import List

class ContentRecommender:
    """
    Service for recommending content based on user preferences and behavior.
    """

    def __init__(self, user_preferences_repository, content_repository):
        self.user_preferences_repository = user_preferences_repository
        self.content_repository = content_repository

    def recommend_content(self, user_id: str) -> List[str]:
        """
        Recommend content for a user based on their preferences.

        Args:
            user_id (str): The ID of the user for whom to recommend content.

        Returns:
            List[str]: A list of recommended content IDs.
        """
        preferences = self.user_preferences_repository.get_preferences(user_id)
        recommended_content = self._fetch_recommended_content(preferences)
        return recommended_content

    def _fetch_recommended_content(self, preferences) -> List[str]:
        """
        Fetch content based on user preferences.

        Args:
            preferences: User preferences object.

        Returns:
            List[str]: A list of recommended content IDs.
        """
        # Logic to fetch content based on preferences
        # This is a placeholder for the actual implementation
        return []  # Replace with actual content fetching logic