class UserAggregate:
    """
    User aggregate managing user lifecycle,
    profile information, and preferences.
    """
    
    def __init__(self, user_id, profile, preferences):
        self.user_id = user_id
        self.profile = profile
        self.preferences = preferences

    def update_profile(self, new_profile):
        self.profile = new_profile

    def update_preferences(self, new_preferences):
        self.preferences = new_preferences

    def get_user_info(self):
        return {
            "user_id": self.user_id,
            "profile": self.profile,
            "preferences": self.preferences
        }