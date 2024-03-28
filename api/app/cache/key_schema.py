import uuid


class KeySchema:
    def __init__(self, hi=None):
        self.hi = hi

    def user_notifications(self, user_id: uuid.UUID | str) -> str:
        return f"user:{user_id}:notifications"

    def notifications(self, notification_id: str | uuid.UUID) -> str:
        return f"notification:{notification_id}"

    # recent chatrooms that a user is a part of that has recieved a message
