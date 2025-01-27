from bson import ObjectId
from datetime import datetime
import pytz

class Audit:
    def __init__(self, username, role, timestamp=None, _id=None):
        # Use MongoDB's ObjectId directly for the id field
        self.id = _id if _id else None  # Use the _id as the MongoDB ObjectId
        self.username = username
        self.role = role
        self.timestamp = timestamp or datetime.now(pytz.utc)

    def to_dict(self):
        return {
            'id': str(self.id),  # Convert the ObjectId to string if needed
            'username': self.username,
            'timestamp': self.timestamp,
            'role': self.role
        }

    def __str__(self):
        return f"{self.username} {self.role} {self.timestamp}"

    @staticmethod
    def from_dict(data):
        # Return the Audit object using MongoDB's ObjectId
        return Audit(
            username=data.get('username'),
            role=data.get('role'),
            timestamp=data.get('timestamp'),
            _id=ObjectId(data.get('_id')) if data.get('_id') else None  # Parse the _id as ObjectId
        )
