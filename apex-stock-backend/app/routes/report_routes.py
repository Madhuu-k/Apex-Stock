from flask import Blueprint, send_file, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
import io
import csv
from app.models import Item, Supplier, ActivityLog
from app.utils import admin_required, log_activity

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/inventory-pdf', methods=['GET'])
@jwt_required()
@admin_required()
def generate_inventory_pdf():
    """
    Generate PDF report of all inventory items
    GET /api/reports/inventory-pdf
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Apex Stock - Inventory Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Metadata
    date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 12))
    
    # Table data
    items = Item.query.all()
    data = [['ID', 'Name', 'Category', 'Quantity', 'Price', 'Status']]
    
    for item in items:
        status = '⚠️ Low Stock' if item.quantity <= item.reorder_level else '✓ OK'
        data.append([
            str(item.id),
            item.name,
            item.category,
            str(item.quantity),
            f"${item.price:.2f}",
            status
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, 'Generated inventory PDF report')
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'inventory_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )


@reports_bp.route('/inventory-csv', methods=['GET'])
@jwt_required()
@admin_required()
def generate_inventory_csv():
    """
    Generate CSV report of all inventory items
    GET /api/reports/inventory-csv
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Header
    writer.writerow(['ID', 'Name', 'Category', 'Quantity', 'Price', 'Reorder Level', 'Supplier', 'Status'])
    
    # Data
    items = Item.query.all()
    for item in items:
        status = 'Low Stock' if item.quantity <= item.reorder_level else 'OK'
        supplier_name = item.supplier.name if item.supplier else 'N/A'
        writer.writerow([
            item.id,
            item.name,
            item.category,
            item.quantity,
            item.price,
            item.reorder_level,
            supplier_name,
            status
        ])
    
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, 'Generated inventory CSV report')
    
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventory_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@reports_bp.route('/low-stock-pdf', methods=['GET'])
@jwt_required()
@admin_required()
def generate_low_stock_pdf():
    """
    Generate PDF report of low stock items
    GET /api/reports/low-stock-pdf
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Apex Stock - Low Stock Alert Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 12))
    
    # Get low stock items
    items = Item.query.filter(Item.quantity <= Item.reorder_level).all()
    
    if not items:
        no_items = Paragraph("No low stock items found!", styles['Normal'])
        elements.append(no_items)
    else:
        data = [['ID', 'Name', 'Current Qty', 'Reorder Level', 'Supplier']]
        
        for item in items:
            supplier_name = item.supplier.name if item.supplier else 'N/A'
            data.append([
                str(item.id),
                item.name,
                str(item.quantity),
                str(item.reorder_level),
                supplier_name
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightpink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, 'Generated low stock PDF report')
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'low_stock_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )


@reports_bp.route('/suppliers-csv', methods=['GET'])
@jwt_required()
@admin_required()
def generate_suppliers_csv():
    """
    Generate CSV report of all suppliers
    GET /api/reports/suppliers-csv
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Header
    writer.writerow(['ID', 'Name', 'Contact Person', 'Email', 'Phone', 'Address', 'Items Count'])
    
    # Data
    suppliers = Supplier.query.all()
    for supplier in suppliers:
        writer.writerow([
            supplier.id,
            supplier.name,
            supplier.contact_person or 'N/A',
            supplier.email or 'N/A',
            supplier.phone or 'N/A',
            supplier.address or 'N/A',
            len(supplier.items)
        ])
    
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, 'Generated suppliers CSV report')
    
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'suppliers_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@reports_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
@admin_required()
def get_activity_logs():
    """
    Get recent activity logs (for dashboard)
    GET /api/reports/activity-logs?limit=20
    """
    limit = int(request.args.get('limit', 20))
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()
    
    return jsonify([log.to_dict() for log in logs]), 200