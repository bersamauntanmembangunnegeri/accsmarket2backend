from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.settings import SiteSetting, WebsiteLayout
from src.models.category import Category
from src.models.product import Product
from src.models.order import Order

admin_bp = Blueprint('admin', __name__)

# Layout Management Routes
@admin_bp.route('/layout', methods=['GET'])
def get_layout():
    """Get website layout configuration"""
    try:
        layout_items = WebsiteLayout.query.order_by(WebsiteLayout.section, WebsiteLayout.sort_order).all()
        
        layout_data = {}
        for item in layout_items:
            if item.section not in layout_data:
                layout_data[item.section] = []
            layout_data[item.section].append(item.to_dict())
        
        return jsonify({
            'success': True,
            'data': layout_data,
            'message': 'Layout configuration retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving layout: {str(e)}'
        }), 500

@admin_bp.route('/layout', methods=['POST'])
def create_layout_item():
    """Create a new layout item"""
    try:
        data = request.get_json()
        
        if not data.get('section') or not data.get('component'):
            return jsonify({
                'success': False,
                'message': 'Section and component are required'
            }), 400
        
        layout_item = WebsiteLayout(
            section=data['section'],
            component=data['component'],
            content=data.get('content', {}),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(layout_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': layout_item.to_dict(),
            'message': 'Layout item created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating layout item: {str(e)}'
        }), 500

@admin_bp.route('/layout/<int:layout_id>', methods=['PUT'])
def update_layout_item(layout_id):
    """Update a layout item"""
    try:
        layout_item = WebsiteLayout.query.get_or_404(layout_id)
        data = request.get_json()
        
        if 'section' in data:
            layout_item.section = data['section']
        if 'component' in data:
            layout_item.component = data['component']
        if 'content' in data:
            layout_item.content = data['content']
        if 'is_active' in data:
            layout_item.is_active = data['is_active']
        if 'sort_order' in data:
            layout_item.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': layout_item.to_dict(),
            'message': 'Layout item updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating layout item: {str(e)}'
        }), 500

@admin_bp.route('/layout/<int:layout_id>', methods=['DELETE'])
def delete_layout_item(layout_id):
    """Delete a layout item"""
    try:
        layout_item = WebsiteLayout.query.get_or_404(layout_id)
        
        db.session.delete(layout_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Layout item deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting layout item: {str(e)}'
        }), 500

# Site Settings Routes
@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get all site settings"""
    try:
        settings = SiteSetting.query.all()
        
        settings_data = {}
        for setting in settings:
            settings_data[setting.key] = setting.to_dict()
        
        return jsonify({
            'success': True,
            'data': settings_data,
            'message': 'Settings retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving settings: {str(e)}'
        }), 500

@admin_bp.route('/settings', methods=['POST'])
def create_setting():
    """Create or update a site setting"""
    try:
        data = request.get_json()
        
        if not data.get('key'):
            return jsonify({
                'success': False,
                'message': 'Key is required'
            }), 400
        
        # Check if setting already exists
        setting = SiteSetting.query.filter_by(key=data['key']).first()
        
        if setting:
            # Update existing setting
            setting.value = data.get('value')
            setting.description = data.get('description')
        else:
            # Create new setting
            setting = SiteSetting(
                key=data['key'],
                value=data.get('value'),
                description=data.get('description')
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': setting.to_dict(),
            'message': 'Setting saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving setting: {str(e)}'
        }), 500

# Dashboard Statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_categories = Category.query.count()
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'categories': {
                    'total': total_categories
                },
                'products': {
                    'total': total_products,
                    'active': active_products,
                    'inactive': total_products - active_products
                },
                'orders': {
                    'total': total_orders,
                    'pending': pending_orders,
                    'completed': completed_orders
                },
                'revenue': {
                    'total': float(total_revenue)
                }
            },
            'message': 'Dashboard statistics retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving dashboard statistics: {str(e)}'
        }), 500

# Bulk Operations
@admin_bp.route('/products/bulk-update', methods=['POST'])
def bulk_update_products():
    """Bulk update products"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        updates = data.get('updates', {})
        
        if not product_ids:
            return jsonify({
                'success': False,
                'message': 'Product IDs are required'
            }), 400
        
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        for product in products:
            for key, value in updates.items():
                if hasattr(product, key):
                    setattr(product, key, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated {len(products)} products'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error bulk updating products: {str(e)}'
        }), 500

