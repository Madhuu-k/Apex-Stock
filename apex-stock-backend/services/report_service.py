from flask import Blueprint, send_file, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
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
    Generate comprehensive PDF report of all inventory items
    GET /api/reports/inventory-pdf
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=20,
        alignment=1
    )
    
    # Title
    title = Paragraph("<b>APEX STOCK</b><br/>Complete Inventory Report", title_style)
    elements.append(title)
    
    # Metadata
    date_text = Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>Report ID: INV-{datetime.now().strftime('%Y%m%d%H%M')}",
        subtitle_style
    )
    elements.append(date_text)
    elements.append(Spacer(1, 20))
    
    # Summary Statistics
    items = Item.query.all()
    total_items = len(items)
    total_quantity = sum(item.quantity for item in items)
    total_value = sum(item.quantity * item.price for item in items)
    low_stock = sum(1 for item in items if item.quantity <= item.reorder_level)
    
    summary_data = [
        ['INVENTORY SUMMARY', ''],
        ['Total Items', str(total_items)],
        ['Total Quantity in Stock', f"{total_quantity:,} units"],
        ['Total Inventory Value', f"${total_value:,.2f}"],
        ['Low Stock Items', f"{low_stock} items need reordering"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Detailed Inventory Table
    detail_header = Paragraph("<b>DETAILED ITEM LIST</b>", styles['Heading2'])
    elements.append(detail_header)
    elements.append(Spacer(1, 12))
    
    # Table headers
    data = [['ID', 'Item Name', 'Category', 'Qty', 'Price', 'Value', 'Supplier', 'Status']]
    
    # Table data
    for item in items:
        status = '⚠ LOW' if item.quantity <= item.reorder_level else '✓ OK'
        supplier_name = item.supplier.name[:15] if item.supplier else 'N/A'
        item_value = item.quantity * item.price
        
        data.append([
            str(item.id),
            item.name[:20],  # Truncate long names
            item.category[:15],
            str(item.quantity),
            f"${item.price:.2f}",
            f"${item_value:.2f}",
            supplier_name,
            status
        ])
    
    # Create table with adjusted column widths
    col_widths = [0.4*inch, 1.8*inch, 1.2*inch, 0.6*inch, 0.8*inch, 0.9*inch, 1.3*inch, 0.7*inch]
    table = Table(data, colWidths=col_widths)
    
    # Table styling
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=1
    )
    footer = Paragraph(
        f"Apex Stock Inventory Management System | Generated on {datetime.now().strftime('%Y-%m-%d')} | Confidential",
        footer_style
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, f'Generated inventory PDF ({total_items} items)')
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'apex_stock_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
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
    
    # Header with metadata
    writer.writerow(['Apex Stock - Inventory Report'])
    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])  # Empty row
    
    # Column headers
    writer.writerow(['ID', 'Item Name', 'Category', 'Quantity', 'Unit Price', 'Total Value', 'Reorder Level', 'Supplier', 'Supplier Email', 'Status', 'Last Updated'])
    
    # Data rows
    items = Item.query.all()
    for item in items:
        status = 'Low Stock' if item.quantity <= item.reorder_level else 'In Stock'
        supplier_name = item.supplier.name if item.supplier else 'N/A'
        supplier_email = item.supplier.email if item.supplier else 'N/A'
        total_value = item.quantity * item.price
        
        writer.writerow([
            item.id,
            item.name,
            item.category,
            item.quantity,
            f"{item.price:.2f}",
            f"{total_value:.2f}",
            item.reorder_level,
            supplier_name,
            supplier_email,
            status,
            item.updated_at.strftime('%Y-%m-%d %H:%M') if item.updated_at else 'N/A'
        ])
    
    # Summary row
    total_items = len(items)
    total_quantity = sum(item.quantity for item in items)
    total_value = sum(item.quantity * item.price for item in items)
    
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Items', total_items])
    writer.writerow(['Total Quantity', total_quantity])
    writer.writerow(['Total Inventory Value', f"${total_value:,.2f}"])
    
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, f'Generated inventory CSV ({total_items} items)')
    
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'apex_stock_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@reports_bp.route('/low-stock-pdf', methods=['GET'])
@jwt_required()
@admin_required()
def generate_low_stock_pdf():
    """
    Generate PDF report of low stock items only
    GET /api/reports/low-stock-pdf
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=12,
        alignment=1
    )
    
    title = Paragraph("<b>⚠ LOW STOCK ALERT REPORT</b>", title_style)
    elements.append(title)
    
    subtitle = Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['Normal']
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Get low stock items
    items = Item.query.filter(Item.quantity <= Item.reorder_level).all()
    
    if not items:
        no_items = Paragraph(
            "<b>✓ GOOD NEWS!</b><br/><br/>No items are currently below reorder level. All inventory levels are healthy.",
            styles['Normal']
        )
        elements.append(no_items)
    else:
        alert = Paragraph(
            f"<b style='color: red;'>{len(items)} ITEMS NEED IMMEDIATE ATTENTION</b>",
            styles['Heading2']
        )
        elements.append(alert)
        elements.append(Spacer(1, 12))
        
        # Table
        data = [['ID', 'Item Name', 'Category', 'Current Qty', 'Reorder Level', 'Shortage', 'Supplier', 'Contact']]
        
        for item in items:
            shortage = item.reorder_level - item.quantity
            supplier_name = item.supplier.name if item.supplier else 'N/A'
            supplier_phone = item.supplier.phone if item.supplier else 'N/A'
            
            data.append([
                str(item.id),
                item.name[:25],
                item.category,
                str(item.quantity),
                str(item.reorder_level),
                str(shortage),
                supplier_name[:15],
                supplier_phone
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.3*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fee2e2')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dc2626')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fee2e2'), colors.HexColor('#fecaca')])
        ]))
        
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, f'Generated low stock PDF ({len(items)} items)')
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'apex_stock_low_stock_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
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
    writer.writerow(['Apex Stock - Suppliers Report'])
    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])
    
    # Column headers
    writer.writerow(['ID', 'Supplier Name', 'Contact Person', 'Email', 'Phone', 'Address', 'Items Supplied', 'Total Value Supplied'])
    
    # Data
    suppliers = Supplier.query.all()
    for supplier in suppliers:
        items_count = len(supplier.items)
        total_value = sum(item.quantity * item.price for item in supplier.items)
        
        writer.writerow([
            supplier.id,
            supplier.name,
            supplier.contact_person or 'N/A',
            supplier.email or 'N/A',
            supplier.phone or 'N/A',
            supplier.address or 'N/A',
            items_count,
            f"{total_value:.2f}"
        ])
    
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Suppliers', len(suppliers)])
    writer.writerow(['Total Items Supplied', sum(len(s.items) for s in suppliers)])
    
    buffer.seek(0)
    
    # Log activity
    user_id = get_jwt_identity()
    log_activity(user_id, 'generated', 'report', None, f'Generated suppliers CSV ({len(suppliers)} suppliers)')
    
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'apex_stock_suppliers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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