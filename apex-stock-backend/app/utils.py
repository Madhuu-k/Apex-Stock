from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User, db

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()  # Check if JWT token is valid
            current_user_id = get_jwt_identity()  # Get user ID from token
            user = User.query.get(current_user_id)
            
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def log_activity(user_id, action, resource_type, resource_id=None, details=None):
    from app.models import ActivityLog
    
    log = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    db.session.add(log)
    db.session.commit()


def validate_request_data(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def get_current_user():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)