from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db

def create_app(config_name='development'):
    """
    Application Factory Pattern
    Creates and configures the Flask app
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)  # SQLAlchemy
    
    # CORS - Allow all origins for development
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    JWTManager(app)  # JWT authentication
    
    # Register blueprints (route modules)
    try:
        from app.routes.auth_routes import auth_bp
        from app.routes.inventory_routes import inventory_bp
        from app.routes.supplier_routes import suppliers_bp
        from app.routes.report_routes import reports_bp
        from app.routes.user_routes import users_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
        app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        app.register_blueprint(users_bp, url_prefix='/api/users')
        
        print("✅ All blueprints registered successfully")
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
        raise
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'message': 'Apex Stock API is running'}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables ready")
    
    return app