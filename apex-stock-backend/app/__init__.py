from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db

def create_app(config_name='development'):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name]) # get current user details
    
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)

    # blueprint for routes
    from app.routes.auth_routes import auth_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.report_routes import reports_bp
    from app.routes.supplier_routes import suppliers_bp
    from app.routes.user_routes import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    @app.route('/api/health')
    def health():
        return {'status' : 'healthy', 'message' : 'Apex stock is working!'}
    
    with app.app_context():
        db.create_all()

    return app

