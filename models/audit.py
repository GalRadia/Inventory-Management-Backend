import uuid
from datetime import datetime

import pytz


class Audit:
    def __init__(self, username, role, timestamp=None,_id=None):
        self.id = str(_id) if _id else None  # Convert ObjectId to string
        self.username = username
        self.role = role
        self.timestamp = timestamp or datetime.now(pytz.utc)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'timestamp': self.timestamp,
            'role': self.role
        }
    def __str__(self):
        return f"{self.username} {self.role} {self.timestamp}"
    @staticmethod
    def from_dict(data):
        return Audit(
            username=data.get('username'),
            role=data.get('role'),
            timestamp=data.get('timestamp'),
            _id=data.get('_id')  # Ensure the id is captured from MongoDB
        )
