from bson import ObjectId
import uuid

class Item:
    def __init__(self, name, price, quantity, description=None, _id=None):
        self.id = str(_id) if _id else None  # Convert ObjectId to string
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description

    def to_dict(self):
        return {
            '_id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }

    def __str__(self):
        return f"{self.name} - {self.quantity} items available at ${self.price} each"

    @staticmethod
    def from_dict(data):
        return Item(
            name=data.get('name'),
            price=data.get('price'),
            quantity=data.get('quantity'),
            description=data.get('description'),
            _id=data.get('_id')  # Ensure the id is captured from MongoDB
        )
