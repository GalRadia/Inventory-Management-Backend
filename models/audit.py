from mongoengine import Document, StringField, DateTimeField
from datetime import datetime


class Audit(Document):
    username = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow())
    role = StringField(required=True)
# Specify the collection name
    meta = {
        'collection': 'Audits'  # Replace with your desired collection name
    }