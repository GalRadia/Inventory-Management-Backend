from models.user import User

class UserDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['Users']

    def create(self, user: User):
        user_dict = user.to_dict()
        result = self.collection.insert_one(user_dict)
        return result.inserted_id

    def get_by_username(self, username: str):
        user_data = self.collection.find_one({"username": username})
        if user_data:
            return User.from_dict(user_data)
        return None

    def update(self, username: str, updated_user: User):
        self.collection.update_one(
            {"username": username},
            {"$set": updated_user.to_dict()}
        )

    def delete(self, username: str):
        self.collection.delete_one({"username": username})


# Example usage:
# db = MongoClient()['your_database']
# user_dao = UserDAO(db)
# new_user = User(username="testuser", password="password", role="admin")
# user_dao.create(new_user)
