from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User
from app.utils import validate_request_data, log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods = ['POST'])
def register():
    data = request.get_json() 

    # validate require fields - check for errors
    is_valid, error = validate_request_data(data, ['username', 'email', 'password'])
    if not is_valid:
        return jsonify({'erorr' : error}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error' : 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error' : 'Email already under use'}), 400
    
    # Create new user
    user = User(
        username = data['username'],
        email = data['email'],
        role = data.get('role', 'staff')  # Default role to Staff
    )

    user.set_password(data['password']) # use set_password function

    db.session.add(user)
    db.session.commit()

    # log the registred activity
    log_activity(user.id, 'created', 'user', user.id, f"User {user.username} registered!!")
    return jsonify({
        'message' : 'User registred successfully',
        'user' : user.to_dict()
    }), 201


@auth_bp.route('/login', methods = ['POST'])
def login():
    data = request.get_json()

    is_valid, error = validate_request_data(data, ['username', 'password'])
    if not is_valid:
        return jsonify({'error': error}), 400
    
    user  = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error':'Invalid username or password'}), 401
    
    access_token = create_access_token(identity=user.id)

    log_activity(user.id, 'logged_in', 'user', user.id, f"User {user.username} logged in")

    return jsonify({
        'message' : 'Login successful',
        'access_token' : access_token,
        'user' : user.to_dict()
    }), 200


@auth_bp.route('/me', methods = ['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error' : 'User not found'}), 404
    
    return jsonify(user.to_dict()), 201


@auth_bp.route('/change-password', methods = ['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    is_valid, error = validate_request_data(data, ['old_password', 'new_password'])
    if not is_valid:
        return jsonify({'error':error}), 400
    
    if not user.check_password(data['old_password']):
        return jsonify({'error':'Current password is incorrect'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()

    log_activity(user.id, 'updated', 'user', user.id, 'Password changed')
    return jsonify({'message':'Password changed successfully'}), 200


     

