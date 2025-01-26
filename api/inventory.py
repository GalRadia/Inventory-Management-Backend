from datetime import datetime, timedelta

import pytz
from werkzeug.exceptions import BadRequest

from api.auth import manager_required
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
    item = item_dao.get_by_id(item_id)  # Use DAO to find item by ID
    if item:
        return jsonify(item.to_json()), 200
    return jsonify({'message': 'Item not found'}), 404


@inventory_bp.route('/search', methods=['GET'])
def search():
    try:
        # Validate that 'name' parameter is provided
        name = request.args.get('name')
        if not name:
            raise BadRequest("Missing required parameter: 'name'")

        # Use DAO to search items by name
        items = item_dao.search_items_by_name(name)

        # Convert the items to JSON format
        response = [item.to_json() for item in items]
        return jsonify(response), 200

    except BadRequest as e:
        # Handle missing or invalid parameters
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Catch all other unexpected errors
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@inventory_bp.route('/insert_item', methods=['POST'])
@manager_required
def insert_item():
    data = request.get_json()
    item = Item.from_dict(data["Item"])  # Create Item object from JSON data
    item_id = item_dao.create(item)  # Use DAO to insert item
    return jsonify({'message': 'Item inserted successfully', 'item_id': str(item_id)}), 201


@inventory_bp.route('/update_item/<item_id>', methods=['PUT'])
@manager_required
def update_item(item_id):
    data = request.get_json()
    item = item_dao.get_by_id(item_id)  # Use DAO to find item
    if item:
        item_dao.update_item(item_id, data)  # Use DAO to update item
        return jsonify({'message': 'Item updated successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404


@inventory_bp.route('/remove/<item_id>', methods=['DELETE'])
@manager_required
def remove_item(item_id):
    item = item_dao.get_by_id(item_id)  # Use DAO to find item
    if item:
        item_dao.remove_item(item_id)  # Use DAO to remove item
        return jsonify({'message': 'Item deleted successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404


@transaction_bp.route('/purchase', methods=['POST'])
@manager_required
def purchase():
    data = request.get_json()
    transaction = Transaction.from_dict(data["Transaction"])  # Create Transaction object from JSON data
    transaction.timestamp = datetime.now(pytz.utc)
    transaction_dao.create_transaction(transaction)  # Use DAO to create transaction
    return jsonify({'message': 'Transaction completed successfully'}), 201




@transaction_bp.route('/transactions', methods=['GET'])
@manager_required
def get_transactions(current_user):
    transactions = transaction_dao.get_transactions_by_user(current_user.username)  # Use DAO to get user transactions
    return jsonify([transaction.to_json() for transaction in transactions]), 200


@transaction_bp.route('/trending', methods=['GET'])
def get_trending_items():
    try:
        # Extract query parameters from request.args
        days = request.args.get('days', default=7, type=int)  # Default to 7 days if not provided
        limit = request.args.get('limit', default=10, type=int)  # Default to 10 items if not provided

        # Calculate the timestamp for the last N days
        last_n_days = datetime.now(pytz.utc) - timedelta(days=days)

        # Define the aggregation pipeline
        pipeline = [
            {"$match": {"timestamp": {"$gte": last_n_days}}},
            {"$group": {"_id": "$item", "total_sales": {"$sum": "$quantity"}}},
            {"$sort": {"total_sales": -1}},
            {"$limit": limit}
        ]

        # Retrieve trending items using DAO
        trending_items = transaction_dao.get_trending_items(pipeline)

        # Prepare the results
        results = []
        for item in trending_items:
            item_details = item_dao.get_by_id(item["_id"])  # Use DAO to fetch item details
            if item_details:
                results.append({
                    "item_id": str(item_details.id),
                    "item_name": item_details.name,
                    "total_sales": item["total_sales"],
                    "total_revenue": item["total_sales"] * item_details.price
                })

        # Return the response as JSON
        return jsonify({"trending_items": results}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


