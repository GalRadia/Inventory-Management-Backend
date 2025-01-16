from models.item import Item

class ItemDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['Items']

    def create(self, item: Item):
        item_dict = item.to_dict()
        result = self.collection.insert_one(item_dict)
        return result.inserted_id

    def get_by_name(self, name: str):
        item_data = self.collection.find_one({"name": name})
        if item_data:
            return Item.from_dict(item_data)
        return None

    def update(self, name: str, updated_item: Item):
        self.collection.update_one(
            {"name": name},
            {"$set": updated_item.to_dict()}
        )

    def delete(self, name: str):
        self.collection.delete_one({"name": name})

    def get_all_items(self):
        items = self.collection.find()
        return [Item.from_dict(item) for item in items]

    def get_item_by_id(self, item_id):
        item = self.collection.find_one({"_id": item_id})
        if item:
            return Item.from_dict(item)

    def search_items_by_name(self, name):
        items = self.collection.find({"name": {"$regex": name, "$options": "i"}})
        return [Item.from_dict(item) for item in items]

    def update_item(self, item_id, data):
        self.collection.update_one(
            {"_id": item_id},
            {"$set": data}
        )

    def remove_item(self, item_id):
        self.collection.delete_one({"_id": item_id})

    def update_item_quantity(self, item_id, param):
        self.collection.update_one(
            {"_id": item_id},
            {"$inc": param}
        )

# Example usage:
# db = MongoClient()['your_database']
# item_dao = ItemDAO(db)
# new_item = Item(name="Test Item", price=10.0, quantity=5)
# item_dao.create(new_item)
