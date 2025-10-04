import os 
from app import create_app
from app.models import db, User

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.cli.command()
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


@app.cli.command()
def seed_admin():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')  # Set a secure password in production

        db.session.add(admin)
        db.session.commit()

        print("✅ Admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  CHANGE PASSWORD IN PRODUCTION!")


@app.cli.command()
def seed_data():
    with app.app_context():
        from app.models import Supplier, Item

        # Create sample suppliers
        supplier1 = Supplier(
            name='Tech Supplies Inc',
            contact_person='John Doe',
            email='john@techsupplies.com',
            phone='555-1234',
            address='123 Tech Street'
        )
        
        supplier2 = Supplier(
            name='Office Mart',
            contact_person='Jane Smith',
            email='jane@officemart.com',
            phone='555-5678',
            address='456 Office Road'
        )
        
        db.session.add(supplier1)
        db.session.add(supplier2)
        db.session.commit()
        
        # Create sample items
        items = [
            Item(name='Laptop', category='Electronics', quantity=15, price=999.99, reorder_level=5, supplier_id=supplier1.id),
            Item(name='Mouse', category='Electronics', quantity=50, price=29.99, reorder_level=10, supplier_id=supplier1.id),
            Item(name='Keyboard', category='Electronics', quantity=3, price=79.99, reorder_level=5, supplier_id=supplier1.id),
            Item(name='Monitor', category='Electronics', quantity=8, price=299.99, reorder_level=5, supplier_id=supplier1.id),
            Item(name='Office Chair', category='Furniture', quantity=12, price=199.99, reorder_level=3, supplier_id=supplier2.id),
            Item(name='Desk', category='Furniture', quantity=2, price=399.99, reorder_level=3, supplier_id=supplier2.id),
            Item(name='Printer Paper', category='Supplies', quantity=100, price=4.99, reorder_level=20, supplier_id=supplier2.id),
        ]

        for item in items:
            db.session.add(item)

        db.session.commit()
        print(f"✅ Seeded {len(items)} items and 2 suppliers!")

        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)