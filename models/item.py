import uuid

class Item:
    def __init__(self,name, price, quantity, description=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }

    def __str__(self):
        return f"{self.name} - {self.quantity} items available at ${self.price} each"

    # Static method for creating an Item from MongoDB document
    @staticmethod
    def from_dict(data):
        return Item(
            name=data.get('name'),
            price=data.get('price'),
            quantity=data.get('quantity'),
            description=data.get('description')
        )