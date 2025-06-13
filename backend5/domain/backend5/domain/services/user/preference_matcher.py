class PreferenceMatcher:
    """
    Service for matching user preferences with available content.
    """

    def __init__(self, user_preferences, content_repository):
        self.user_preferences = user_preferences
        self.content_repository = content_repository

    def match_preferences(self):
        """
        Match user preferences with available content and return recommendations.
        """
        recommendations = []
        for preference in self.user_preferences:
            matched_content = self.content_repository.find_by_preference(preference)
            recommendations.extend(matched_content)
        return recommendations

    def update_preferences(self, new_preferences):
        """
        Update user preferences with new values.
        """
        self.user_preferences = new_preferences

    def clear_preferences(self):
        """
        Clear all user preferences.
        """
        self.user_preferences = []