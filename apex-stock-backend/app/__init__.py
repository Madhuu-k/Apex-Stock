from flask import Flask, request, Response
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
    
    # Load configuration - this already includes JWT settings
    app.config.from_object(config[config_name])
    
    # DISABLE STRICT SLASHES - prevents 308 redirects that lose auth headers
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    db.init_app(app)
    
    # CRITICAL: CORS must be set up BEFORE JWT and blueprints
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:5173", "http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})
    
    # Handle OPTIONS requests BEFORE JWT validation
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = Response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
    
    # ONLY set JWT configs that are NOT in config.py
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    
    jwt = JWTManager(app)
    
    # Handle JWT errors gracefully with debug info
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        print(f"🔴 JWT Unauthorized: {callback}")
        return {'error': 'Missing or invalid token'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"🔴 JWT Invalid Token: {error_string}")
        return {'error': f'Invalid token: {error_string}'}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"🔴 JWT Expired Token")
        return {'error': 'Token has expired'}, 401
    
    # Import blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.supplier_routes import suppliers_bp
    from app.routes.report_routes import reports_bp
    from app.routes.user_routes import users_bp
    
    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    print("✅ All blueprints registered")
    print(f"✅ JWT Secret Key configured: {app.config.get('JWT_SECRET_KEY')[:10]}...")
    
    # Health check endpoint (no auth required)
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def health():
        return {'status': 'healthy', 'message': 'Apex Stock API is running'}, 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database ready")
    
    return app
