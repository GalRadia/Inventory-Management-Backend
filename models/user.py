from mongoengine import Document, StringField


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)

    def __str__(self):
        return f"User: {self.username}"
