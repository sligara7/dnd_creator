class UserPreferences:
    """
    Represents user preferences for the D&D character creator.
    This class encapsulates various settings and preferences
    that a user can configure to tailor their experience.
    """

    def __init__(self, theme: str, language: str, notifications_enabled: bool):
        self.theme = theme  # User's preferred theme (e.g., 'dark', 'light')
        self.language = language  # User's preferred language (e.g., 'en', 'es')
        self.notifications_enabled = notifications_enabled  # Notification preference

    def update_preferences(self, theme: str = None, language: str = None, notifications_enabled: bool = None):
        """
        Update user preferences based on provided values.
        """
        if theme is not None:
            self.theme = theme
        if language is not None:
            self.language = language
        if notifications_enabled is not None:
            self.notifications_enabled = notifications_enabled

    def to_dict(self) -> dict:
        """
        Convert the user preferences to a dictionary representation.
        """
        return {
            "theme": self.theme,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
        }