from app import create_app
from app.models import db, User, Supplier, Item

app = create_app()

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")

def seed_admin():
    """Create default admin user"""
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("⚠️  Admin user already exists!")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            return
        
        # Create admin
        admin = User(
            username='admin',
            email='admin@apexstock.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  CHANGE PASSWORD IN PRODUCTION!")

def seed_data():
    """Seed database with sample data for testing"""
    with app.app_context():
        # Check if data already exists
        if Supplier.query.count() > 0:
            print("⚠️  Sample data already exists!")
            return
        
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

def reset_db():
    """Drop all tables and recreate"""
    with app.app_context():
        print("⚠️  WARNING: This will delete ALL data!")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Cancelled")
            return
        
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python seed.py init       - Create database tables")
        print("  python seed.py admin      - Create admin user")
        print("  python seed.py data       - Add sample data")
        print("  python seed.py all        - Do all of the above")
        print("  python seed.py reset      - Reset database (DANGEROUS)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'admin':
        seed_admin()
    elif command == 'data':
        seed_data()
    elif command == 'all':
        init_db()
        seed_admin()
        seed_data()
    elif command == 'reset':
        reset_db()
    else:
        print(f"❌ Unknown command: {command}")