import uuid


class User:
    def __init__(self, username, password, role,_id=None):
        self.id = str(_id) if _id else None  # Convert ObjectId to string
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'id': self.id,
        }

    def __str__(self):
        return f"User: {self.username}"

    # Static method for creating a User from MongoDB document
    @staticmethod
    def from_dict(data):
        return User(
            username=data.get('username'),
            password=data.get('password'),
            role=data.get('role'),
            _id=data.get('_id')  # Ensure the id is captured from MongoDB

        )
