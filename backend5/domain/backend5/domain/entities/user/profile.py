class UserProfile:
    """
    Represents a user profile in the system, containing personal information
    and settings related to the user.
    """

    def __init__(self, user_id: str, username: str, email: str, bio: str = "", avatar_url: str = ""):
        self.user_id = user_id  # Unique identifier for the user
        self.username = username  # Username chosen by the user
        self.email = email  # User's email address
        self.bio = bio  # Short biography or description of the user
        self.avatar_url = avatar_url  # URL to the user's avatar image

    def update_profile(self, username: str = None, email: str = None, bio: str = None, avatar_url: str = None):
        """
        Updates the user's profile information.
        """
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if bio is not None:
            self.bio = bio
        if avatar_url is not None:
            self.avatar_url = avatar_url

    def __repr__(self):
        return f"UserProfile(user_id={self.user_id}, username={self.username}, email={self.email})"