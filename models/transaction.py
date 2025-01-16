import uuid
from datetime import datetime
from models.item import Item

class Transaction:
    def __init__(self, item, quantity, price, buyer, timestamp=None):
        self.item = item  # This will be an instance of Item (or its ObjectId in PyMongo)
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp or datetime.utcnow()
        self.buyer = buyer

    def to_dict(self):
        # Convert item to its ObjectId or its dict representation
        return {
            'item': self.item.to_dict() if isinstance(self.item, Item) else self.item,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp,
            'buyer': self.buyer
        }

    def __str__(self):
        return f'{self.item} {self.quantity} {self.price} {self.timestamp} {self.buyer}'

    # Static method for creating a Transaction from MongoDB document
    @staticmethod
    def from_dict(data):
        # Item can be passed as ObjectId or as an Item instance
        item = data.get('item')  # Assuming this could be an ObjectId or Item
        return Transaction(
            item=item,
            quantity=data.get('quantity'),
            price=data.get('price'),
            buyer=data.get('buyer'),
            timestamp=data.get('timestamp')
        )
