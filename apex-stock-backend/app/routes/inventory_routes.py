from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Item, ActivityLog
from app.utils import validate_request_data, log_activity

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_items():
    """
    Get all inventory items
    GET /api/inventory
    Query params: ?category=... (optional filter)
    """
    category = request.args.get('category')
    
    if category:
        items = Item.query.filter_by(category=category).all()
    else:
        items = Item.query.all()
    
    return jsonify([item.to_dict() for item in items]), 200


@inventory_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    """
    Get single item by ID
    GET /api/inventory/123
    """
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item.to_dict()), 200


@inventory_bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
    """
    Create new inventory item
    POST /api/inventory
    Body: { "name": "...", "category": "...", "quantity": 100, "price": 29.99, "supplier_id": 1 }
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    
    print(f"📝 Creating item with data: {data}")  # DEBUG
    
    # Validate required fields
    is_valid, error = validate_request_data(data, ['name', 'category', 'quantity', 'price'])
    if not is_valid:
        print(f"❌ Validation error: {error}")  # DEBUG
        return jsonify({'error': error}), 400
    
    try:
        # Create item
        item = Item(
            name=data['name'],
            category=data['category'],
            quantity=data['quantity'],
            price=data['price'],
            reorder_level=data.get('reorder_level', 10),
            supplier_id=data.get('supplier_id') if data.get('supplier_id') else None
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Log activity
        log_activity(user_id, 'created', 'item', item.id, f"Added item: {item.name}")
        
        print(f"✅ Item created successfully: {item.name}")  # DEBUG
        
        return jsonify({
            'message': 'Item created successfully',
            'item': item.to_dict()
        }), 201
    except Exception as e:
        print(f"❌ Exception creating item: {str(e)}")  # DEBUG
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """
    Update existing item
    PUT /api/inventory/123
    Body: { "quantity": 150, "price": 24.99 } (any fields to update)
    """
    item = Item.query.get(item_id)
    user_id = get_jwt_identity()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        item.name = data['name']
    if 'category' in data:
        item.category = data['category']
    if 'quantity' in data:
        item.quantity = data['quantity']
    if 'price' in data:
        item.price = data['price']
    if 'reorder_level' in data:
        item.reorder_level = data['reorder_level']
    if 'supplier_id' in data:
        item.supplier_id = data['supplier_id'] if data['supplier_id'] else None
    
    db.session.commit()
    
    # Log activity
    log_activity(user_id, 'updated', 'item', item.id, f"Updated item: {item.name}")
    
    return jsonify({
        'message': 'Item updated successfully',
        'item': item.to_dict()
    }), 200


@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """
    Delete item
    DELETE /api/inventory/123
    """
    item = Item.query.get(item_id)
    user_id = get_jwt_identity()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    
    # Log activity
    log_activity(user_id, 'deleted', 'item', item_id, f"Deleted item: {item_name}")
    
    return jsonify({'message': 'Item deleted successfully'}), 200


@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_items():
    """
    Get items that need reordering
    GET /api/inventory/low-stock
    """
    items = Item.query.filter(Item.quantity <= Item.reorder_level).all()
    
    return jsonify([item.to_dict() for item in items]), 200


@inventory_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_inventory_stats():
    """
    Get inventory statistics for dashboard
    GET /api/inventory/stats
    """
    total_items = Item.query.count()
    total_value = db.session.query(db.func.sum(Item.quantity * Item.price)).scalar() or 0
    low_stock_count = Item.query.filter(Item.quantity <= Item.reorder_level).count()
    categories = db.session.query(Item.category, db.func.count(Item.id)).group_by(Item.category).all()
    
    return jsonify({
        'total_items': total_items,
        'total_value': round(total_value, 2),
        'low_stock_count': low_stock_count,
        'categories': [{'name': cat, 'count': count} for cat, count in categories]
    }), 200