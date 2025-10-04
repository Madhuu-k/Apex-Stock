from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(50), nullable = False)
    role = db.Column(db.String(20), default = 'staff') # Admin or Staff
    created_at = db.Column(db.DateTime, default = datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email,
            'role' : self.role,
            'created_at' : self.created_at.isoformat()
        }
    

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    contact_person = db.Column(db.String(300))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    
    items = db.relationship('Item', backref = 'supplier', lazy = True)

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'contact_person' : self.contact_person,
            'email' : self.email,
            'phone' : self.phone,
            'address' : self.address,
            'created_at' :self.created_at.isoformat(),
            'items_count' : len(self.items)
        }


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False) 
    category = db.Column(db.String(200), nullable = False) 
    quantity = db.Column(db.Integer, nullable = False, default = 0)
    price = db.Column(db.Float, nullable = False)
    reorder_level = db.Column(db.Integer, nullable = False) 
    supplier_id = db.Column(db.Integer,db.ForeignKey('suppliers.id')) 
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'price': self.price,
            'reorder_level': self.reorder_level,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'is_low_stock': self.quantity <= self.reorder_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)  # 'created', 'updated', 'deleted'
    resource_type = db.Column(db.String(50), nullable=False)  # 'item', 'supplier', 'user'
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # Extra info about the action
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.username if self.user else 'System',
            'action': self.action,
            'resource_type': self.resource_type,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }