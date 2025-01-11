from mongoengine import Document, StringField, IntField,FloatField

class Item(Document):
    name = StringField(required=True, unique=True)
    price = FloatField(required=True,min_value=0)
    quantity = IntField(required=True)
    description = StringField()


    def __str__(self):
        return f"{self.name} - {self.quantity} items available at ${self.price} each"

