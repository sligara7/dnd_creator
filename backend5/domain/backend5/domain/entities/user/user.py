class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email

    def __repr__(self):
        return f"User(user_id={self.user_id}, username={self.username}, email={self.email})"

    def update_email(self, new_email: str):
        self.email = new_email

    def change_username(self, new_username: str):
        self.username = new_username

    # Additional user-related methods can be added here.