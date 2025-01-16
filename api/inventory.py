from datetime import datetime, timedelta

from api.auth import  manager_required
from flask import Blueprint, request, jsonify
from models.item import Item
from models.transaction import Transaction
from dal import ItemDAO, TransactionDAO
from mongoDB_manager import MongoConnectionHolder

inventory_bp = Blueprint('inventory', __name__)
transaction_bp = Blueprint('transaction', __name__)

# Initialize DAOs
db = MongoConnectionHolder.get_db()
item_dao = ItemDAO(db)
transaction_dao = TransactionDAO(db)

@inventory_bp.route('/items', methods=['GET'])
def get_items():
    items = item_dao.get_all_items()  # Use DAO to retrieve items
    return jsonify([item.to_json() for item in items]), 200

@inventory_bp.route('/items/<item_id>', methods=['GET'])
def get_item_by_id(item_id):
    item = item_dao.get_item_by_id(item_id)  # Use DAO to find item by ID
    if item:
        return jsonify(item.to_json()), 200
    return jsonify({'message': 'Item not found'}), 404

@inventory_bp.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    items = item_dao.search_items_by_name(name)  # Use DAO to search items by name
    return jsonify([item.to_json() for item in items]), 200

@inventory_bp.route('/insert_item', methods=['POST'])
@manager_required
def insert_item():
    data = request.get_json()
    item = Item(
        name=data.get('name'),
        price=data.get('price'),
        quantity=data.get('quantity'),
        description=data.get('description')
    )
    item_id = item_dao.create(item)  # Use DAO to insert item
    return jsonify({'message': 'Item inserted successfully', 'item_id': str(item_id)}), 201

@inventory_bp.route('/update_item/<item_id>', methods=['PUT'])
@manager_required
def update_item(item_id):
    data = request.get_json()
    item = item_dao.get_item_by_id(item_id)  # Use DAO to find item
    if item:
        item_dao.update_item(item_id, data)  # Use DAO to update item
        return jsonify({'message': 'Item updated successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404

@inventory_bp.route('/remove/<item_id>', methods=['DELETE'])
@manager_required
def remove_item(item_id):
    item = item_dao.get_item_by_id(item_id)  # Use DAO to find item
    if item:
        item_dao.remove_item(item_id)  # Use DAO to remove item
        return jsonify({'message': 'Item deleted successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404

@transaction_bp.route('/purchase', methods=['POST'])
@manager_required
def purchase(current_user):
    data = request.get_json()
    item_id = data.get('id')
    purchase_quantity = data.get('quantity')
    user_name = current_user.username
    return create_transaction(user_name, item_id, purchase_quantity)

@transaction_bp.route('/transactions', methods=['GET'])
@manager_required
def get_transactions(current_user):
    transactions = transaction_dao.get_transactions_by_user(current_user.username)  # Use DAO to get user transactions
    return jsonify([transaction.to_json() for transaction in transactions]), 200

@transaction_bp.route('/trending', methods=['GET'])
def get_trending_items():
    data = request.get_json()
    days = data.get('days', 7)
    last_n_days = datetime.utcnow() - timedelta(days=days)
    limit = data.get('limit', 10)

    pipeline = [
        {"$match": {"timestamp": {"$gte": last_n_days}}},
        {"$group": {"_id": "$item", "total_sales": {"$sum": "$quantity"}}},
        {"$sort": {"total_sales": -1}},
        {"$limit": limit}
    ]

    trending_items = transaction_dao.get_trending_items(pipeline)  # Use DAO to aggregate trending items

    results = []
    for item in trending_items:
        item_details = item_dao.get_item_by_id(item["_id"])  # Use DAO to find item details
        if item_details:
            results.append({
                "item_id": str(item_details.id),
                "item_name": item_details.name,
                "total_sales": item["total_sales"],
                "total_revenue": item["total_sales"] * item_details.price
            })

    return jsonify({"trending_items": results}), 200

def create_transaction(user_name, item_id, purchase_quantity):
    item = item_dao.get_item_by_id(item_id)  # Use DAO to find item
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    if item.quantity < purchase_quantity:
        return jsonify({'message': 'Not enough stock available'}), 400

    item_dao.update_item_quantity(item_id, item.quantity - purchase_quantity)  # Use DAO to update quantity

    transaction = Transaction(item=item, quantity=purchase_quantity, price=item.price, buyer=user_name)
    transaction_id = transaction_dao.create_transaction(transaction)  # Use DAO to create transaction


    return jsonify({'message': 'Transaction completed successfully', 'transaction_id': str(transaction_id)}), 201
