from bson import ObjectId

from models.user import User


class UserDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['Users']

    def create(self, user: User):
        user_dict = user.to_dict()
        result = self.collection.insert_one(user_dict)
        return result.inserted_id

    def get_by_id(self, user_id):
        user_data = self.collection.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_data)

    def update(self, username: str, updated_user: User):
        self.collection.update_one(
            {"username": username},
            {"$set": updated_user.to_dict()}
        )

    def delete(self, username: str):
        self.collection.delete_one({"username": username})

    def get_all(self):
        users = self.collection.find()
        return [User.from_dict(user) for user in users]

    def get_by_username(self, param):
        user_data = self.collection.find_one({"username": param})
        return User.from_dict(user_data) if user_data else None
