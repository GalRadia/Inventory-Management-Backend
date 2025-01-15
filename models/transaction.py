
from mongoengine import Document, IntField, ReferenceField, DateTimeField,FloatField,StringField
from datetime import datetime

from models.item import Item


class Transaction(Document):
    item = ReferenceField(Item, required=True)
    quantity = IntField(required=True, min_value=1)
    price = FloatField(required=True, min_value=0)
    timestamp = DateTimeField(default=datetime.utcnow())
    buyer =StringField(required=True)
    # Specify the collection name
    meta = {
        'collection': 'Transactions'  # Replace with your desired collection name
    }
    def to_json(self):
        return {
            'item': self.item.to_json(),
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp,
            'buyer': self.buyer
        }
    def __str__(self):
        return f'{self.item} {self.quantity} {self.price} {self.timestamp} {self.buyer}'

