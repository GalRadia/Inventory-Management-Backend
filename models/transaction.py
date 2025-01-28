import uuid
from datetime import datetime
from models.item import Item


class Transaction:
    def __init__(self, item_id, quantity, price, buyer, timestamp=None, _id=None):
        self.id = str(_id) if _id else None  # Convert ObjectId to string
        self.item_id = item_id  # This will be an instance of Item (or its ObjectId in PyMongo)
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp or datetime.utcnow()
        self.buyer = buyer


    def to_dict(self):
        # Convert item to its ObjectId or its dict representation
        return {
            'id': self.id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp,
            'buyer': self.buyer
        }


    def __str__(self):
        return f'{self.item_id} {self.quantity} {self.price} {self.timestamp} {self.buyer}'


    # Static method for creating a Transaction from MongoDB document
    @staticmethod
    def from_dict(data):
        # Item can be passed as ObjectId or as an Item instance
        return Transaction(
            item_id=data.get('item_id'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            buyer=data.get('buyer'),
            timestamp=data.get('timestamp'),
            _id=data.get('_id')  # Ensure the id is captured from MongoDB

        )
