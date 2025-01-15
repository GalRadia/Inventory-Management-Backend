from mongoengine import Document, StringField, IntField,FloatField

class Item(Document):
    name = StringField(required=True, unique=True)
    price = FloatField(required=True,min_value=0)
    quantity = IntField(required=True)
    description = StringField()
    # Specify the collection name
    meta = {
        'collection': 'Items'  # Replace with your desired collection name
    }

    def __str__(self):
        return f"{self.name} - {self.quantity} items available at ${self.price} each"
    def to_json(self):
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }


