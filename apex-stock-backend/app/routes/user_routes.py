from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.utils import admin_required, validate_request_data, log_activity

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user(user_id):
    """
    Get single user by ID (Admin only)
    GET /api/users/123
    """
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_user():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate required fields
    is_valid, error = validate_request_data(data, ['username', 'email', 'password', 'role'])
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate role
    if data['role'] not in ['admin', 'staff']:
        return jsonify({'error': 'Invalid role. Must be "admin" or "staff"'}), 400
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Log activity
    log_activity(current_user_id, 'created', 'user', user.id, 
                 f"Admin created user: {user.username} ({user.role})")
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_user(user_id):
    user = User.query.get(user_id)
    current_user_id = get_jwt_identity()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'username' in data:
        # Check if username is taken
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # Check if email is taken
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already registered'}), 400
        user.email = data['email']
    
    if 'role' in data:
        if data['role'] not in ['admin', 'staff']:
            return jsonify({'error': 'Invalid role'}), 400
        user.role = data['role']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    # Log activity
    log_activity(current_user_id, 'updated', 'user', user.id, 
                 f"Admin updated user: {user.username}")
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user(user_id):
    """
    Delete user (Admin only)
    DELETE /api/users/123
    """
    user = User.query.get(user_id)
    current_user_id = get_jwt_identity()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent admin from deleting themselves
    if user.id == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # Log activity
    log_activity(current_user_id, 'deleted', 'user', user_id, 
                 f"Admin deleted user: {username}")
    
    return jsonify({'message': 'User deleted successfully'}), 200


@users_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required()
def get_user_stats():
    """
    Get user statistics (Admin only)
    GET /api/users/stats
    """
    total_users = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    staff_count = User.query.filter_by(role='staff').count()
    
    return jsonify({
        'total_users': total_users,
        'admins': admin_count,
        'staff': staff_count
    }), 200