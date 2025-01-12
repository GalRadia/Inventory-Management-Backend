from datetime import datetime, timedelta

from api.auth import token_required
from models.item import Item
from flask import Blueprint, request, jsonify

from models.transaction import Transaction

inventory_bp = Blueprint('inventory', __name__)
transaction_bp = Blueprint('transaction', __name__)


@inventory_bp.route('/items', methods=['GET'])
def get_items():
    items = Item.objects()  # Retrieves all items from the database
    return jsonify([item.to_json() for item in items]), 200


@inventory_bp.route('/items/<item_id>', methods=['GET'])
def get_item_by_id(item_id):
    item = Item.objects(id=item_id).first()
    if item:
        return jsonify(item.to_json()), 200
    return jsonify({'message': 'Item not found'}), 404


# @inventory_bp.route('/items/<item_name>', methods=['GET'])
# def get_item_by_name(item_name):
#     item = Item.objects(name=item_name).first()
#     if item:
#         return jsonify(item.to_json()), 200
#     return jsonify({'message': 'Item not found'}), 404

@inventory_bp.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    items = Item.objects(name__icontains=name)
    return jsonify([item.to_json() for item in items]), 200


@inventory_bp.route('/insert_item', methods=['POST'])
def insert_item():
    data = request.get_json()
    item = Item(
        name=data.get('name'),
        price=data.get('price'),
        quantity=data.get('quantity'),
        description=data.get('description')

    )
    item.save()  # Save the item to the MongoDB database
    return jsonify({'message': 'Item inserted successfully', 'item_id': str(item.id)}), 201


@inventory_bp.route('/update_item/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    item = Item.objects(id=item_id).first()  # Find item by id
    if item:
        item.update(**data)


@inventory_bp.route('/remove/<item_id>', methods=['DELETE'])
def remove_item(item_id):
    item = Item.objects(id=item_id).first()  # Find item by id
    if item:
        item.delete()  # Delete the item from the database
        return jsonify({'message': 'Item deleted successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404


@transaction_bp.route('/purchase', methods=['POST'])
@token_required(pass_user=True)
def purchase(current_user):
    data = request.get_json()
    item_id = data.get('id')
    purchase_quantity = data.get('quantity')
    user_name = current_user.username
    return create_transaction(user_name,item_id, purchase_quantity)
@transaction_bp.route('/transactions', methods=['GET'])
@token_required(pass_user=False)
def get_transactions():
    transactions = Transaction.objects()
    return jsonify([transaction.to_json() for transaction in transactions]), 200

@transaction_bp.route('/trending', methods=['GET'])
@token_required(pass_user=False)
def get_trending_items():
    # Define the time range for "trending" (last 7 days)
    data = request.get_json()
    days = data.get('days', 7)
    last_n_days = datetime.utcnow() - timedelta(days=days)
    limit = data.get('limit', 10)

    # Aggregate transactions to count purchases per item in the last 7 days
    pipeline = [
        {"$match": {"timestamp": {"$gte": last_n_days}}},
        {"$group": {"_id": "$item", "total_sales": {"$sum": "$quantity"}}},
        {"$sort": {"total_sales": -1}},  # Sort by total sales in descending order
        {"$limit": limit}  # Limit the result to top 10 trending items
    ]

    trending_items = Transaction.objects.aggregate(pipeline)

    # Format the response
    results = []
    for item in trending_items:
        # Fetch item details
        item_details = Item.objects(id=item["_id"]).first()
        if item_details:
            results.append({
                "item_id": str(item_details.id),
                "item_name": item_details.name,
                "total_sales": item["total_sales"],
                "total_revenue": item["total_sales"] * item_details.price
            })

    return jsonify({"trending_items": results}), 200


def create_transaction(user_name,item_id, purchase_quantity):
    # Find the item in the database
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    # Check if the item has enough quantity
    if item.quantity < purchase_quantity:
        return jsonify({'message': 'Not enough stock available'}), 400

    # Deduct the quantity from the item
    item.quantity -= purchase_quantity
    item.save()

    # Create a new transaction record
    transaction = Transaction(item=item, quantity=purchase_quantity, price=item.price, buyer=user_name)
    transaction.save()

    return jsonify({'message': 'Transaction completed successfully', 'transaction_id': str(transaction.id)}), 201
