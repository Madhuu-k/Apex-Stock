from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Supplier
from app.utils import validate_request_data, log_activity, admin_required

suppliers_bp = Blueprint('supplier',__name__)

@suppliers_bp.route('/', methods = ['GET'])
@jwt_required()
def get_all_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([supplier.to_dict() for supplier in suppliers]), 200


@suppliers_bp.route('<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error' : 'Supplier not found'}), 404
    return jsonify(supplier.to_dict()), 200


@suppliers_bp.route('/', methods = ['POST'])
@jwt_required()
def create_supplier():
    data = request.get_json()
    user_id = get_jwt_identity()

    is_valid, error = validate_request_data(data, ['name'])
    if not is_valid:
        return jsonify({'error' : error}), 400
    
    # Crate supplier
    supplier = Supplier(
        name = data['name'],
        contact_person = data.get('contact_person'),
        email = data.get('email'),
        phone = data.get('phone'),
        address = data.get('address')
    )

    db.session.add(supplier)
    db.session.commit()

    log_activity(user_id, 'created', 'supplier', supplier.id, f"Added supplier {supplier.name}")

    return jsonify({
        'message' : 'Supplier added successfully',
        'supplier' : supplier.to_dict()
    }), 201


@suppliers_bp.route('/<int:supplier_id>', methods = ['POST'])
@jwt_required()
def update_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    user_id = get_jwt_identity()

    if not supplier:
        return jsonify({'error' : 'Supplier nnot found'}), 404
    
    data = request.get_json()

    if 'name' in data:
        supplier.name = data['name']

    if 'contact_person' in data:
        supplier.contact_person = data['contact_person']

    if 'email' in data:
        supplier.email = data['email']

    if 'phone' in data:
        supplier.phone = data['phone']

    if 'address' in data:
        supplier.address = data['address']

    db.session.commit()

    log_activity(user_id, 'updated', 'supplier', supplier.id, f"Updated supplier {supplier.name}")

    return jsonify({
        'message' : 'Supplier updates sucessfully',
        'supplier' : supplier.to_dict()
    }), 200


@suppliers_bp.route('/<int:supplier_id>', methods = ['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    user_id = get_jwt_identity()

    if not supplier:
        return jsonify({'error' : 'Supplier not found'}), 404
    
    if supplier.items:
        return jsonify({'error' : 'Cannot delete supplier with associated items',
                        'items_count' : len(supplier.items)}), 400
    
    supplier_name = supplier.name
    db.session.delete(supplier)
    db.session.commit()

    log_activity(user_id, 'deleted', 'supplier', supplier.id, f"Deletes supplier: {supplier_name}")

    return jsonify({'message' : 'Supplier deleted successfully'}), 200


@suppliers_bp.route('<int:supplier_id>/items', methods = ['GET'])
@jwt_required()
def get_supplier_items(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error' : 'Supplier not found'}), 404
    
    return jsonify([item.to_dict() for item in supplier.items]), 200