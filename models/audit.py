import uuid
from datetime import datetime

class Audit:
    def __init__(self, username, role, timestamp=None):
        self._id=str(uuid.uuid4())
        self.username = username
        self.role = role
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        return {
            '_id':self._id,
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
            timestamp=data.get('timestamp')
        )
