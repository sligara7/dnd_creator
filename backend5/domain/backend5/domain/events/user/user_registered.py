class UserRegisteredEvent:
    """
    Event published when a new user registers in the system.
    Contains user information relevant to the registration process.
    """

    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email

    def __repr__(self):
        return f"UserRegisteredEvent(user_id={self.user_id}, username={self.username}, email={self.email})"