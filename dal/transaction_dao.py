from bson import ObjectId
from pymongo import MongoClient
from models.transaction import Transaction

class TransactionDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['Transactions']

    def create(self, transaction: Transaction):
        transaction_dict = transaction.to_dict()
        result = self.collection.insert_one(transaction_dict)
        return result.inserted_id
    def get_by_id(self, transaction_id: str):
        transaction_data = self.collection.find_one({"_id": ObjectId(transaction_id)})
        return Transaction.from_dict(transaction_data)

    def get_by_buyer(self, buyer: str):
        transactions = self.collection.find({"buyer": buyer})
        return [Transaction.from_dict(transaction) for transaction in transactions]

    def get_by_item(self, item_id: str):
        transactions = self.collection.find({"item": ObjectId(item_id)})
        return [Transaction.from_dict(transaction) for transaction in transactions]

    def update(self, transaction_id: str, updated_transaction: Transaction):
        self.collection.update_one(
            {"_id": ObjectId(transaction_id)},
            {"$set": updated_transaction.to_dict()}
        )
    def get_all(self):
        transactions = self.collection.find()
        return [Transaction.from_dict(transaction) for transaction in transactions]

    def delete(self, transaction_id: str):
        self.collection.delete_one({"_id": ObjectId(transaction_id)})

    def get_transactions_by_user(self, username):
        transactions = self.collection.find({"buyer": username})
        return [Transaction.from_dict(transaction) for transaction in transactions]

    def get_trending_items(self, pipeline):
        return self.collection.aggregate(pipeline)

    def create_transaction(self, transaction):
        transaction_dict = transaction.to_dict()
        result = self.collection.insert_one(transaction_dict)
        return result.inserted_id
    def remove_transaction(self, transaction_id):
        self.collection.delete_one({"_id": ObjectId(transaction_id)})

# Example usage:
# db = MongoClient()['your_database']
# transaction_dao = TransactionDAO(db)
# new_transaction = Transaction(item="item_id", quantity=2, price=20.0, buyer="buyer_id")
# transaction_dao.create(new_transaction)
