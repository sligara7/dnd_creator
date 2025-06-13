class PreferencesUpdatedEvent:
    """
    Event published when user preferences are updated.
    
    Attributes:
        user_id (str): The ID of the user whose preferences were updated.
        updated_preferences (dict): The updated preferences for the user.
        timestamp (datetime): The time when the preferences were updated.
    """

    def __init__(self, user_id: str, updated_preferences: dict, timestamp: datetime):
        self.user_id = user_id
        self.updated_preferences = updated_preferences
        self.timestamp = timestamp

    def __repr__(self):
        return f"<PreferencesUpdatedEvent user_id={self.user_id} timestamp={self.timestamp}>"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "updated_preferences": self.updated_preferences,
            "timestamp": self.timestamp.isoformat(),
        }