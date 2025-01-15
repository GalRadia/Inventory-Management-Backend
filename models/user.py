from enum import Enum

from mongoengine import Document, StringField


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    role = StringField(required=True)
    # Specify the collection name
    meta = {
        'collection': 'Users'  # Replace with your desired collection name
    }

    def __str__(self):
        return f"User: {self.username}"
