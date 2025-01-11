
from mongoengine import Document, IntField, ReferenceField, DateTimeField,FloatField
from datetime import datetime

from models.item import Item


class Transaction(Document):
    item = ReferenceField(Item, required=True)
    quantity = IntField(required=True, min_value=1)
    price = FloatField(required=True, min_value=0)
    timestamp = DateTimeField(default=datetime.utcnow())

    def __str__(self):
        return f"{self.quantity} {self.item.name} - {self.timestamp}"
