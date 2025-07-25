from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.product import Product
from src.models.category import Category
from src.models.vendor import Vendor

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        vendor_id = request.args.get('vendor_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Build query
        query = Product.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if vendor_id:
            query = query.filter_by(vendor_id=vendor_id)
        
        # Order by product_id for consistency
        query = query.order_by(Product.product_id.desc())
        
        # Paginate
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        products_data = []
        for product in products.items:
            products_data.append(product.to_dict_legacy())
        
        return jsonify({
            'success': True,
            'data': products_data,
            'pagination': {
                'page': products.page,
                'pages': products.pages,
                'per_page': products.per_page,
                'total': products.total,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            },
            'message': 'Products retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving products: {str(e)}'
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        return jsonify({
            'success': True,
            'data': product.to_dict_legacy(),
            'message': 'Product retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving product: {str(e)}'
        }), 500

@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('price_per_pc'):
            return jsonify({
                'success': False,
                'message': 'Name and price_per_pc are required'
            }), 400
        
        # Validate category exists
        if not data.get('category_id'):
            return jsonify({
                'success': False,
                'message': 'Category ID is required'
            }), 400
            
        category = Category.query.filter_by(category_id=data['category_id']).first()
        if not category:
            return jsonify({
                'success': False,
                'message': 'Category not found'
            }), 400
        
        # Validate vendor exists
        if not data.get('vendor_id'):
            return jsonify({
                'success': False,
                'message': 'Vendor ID is required'
            }), 400
            
        vendor = Vendor.query.filter_by(vendor_id=data['vendor_id']).first()
        if not vendor:
            return jsonify({
                'success': False,
                'message': 'Vendor not found'
            }), 400
        
        product = Product(
            category_id=data['category_id'],
            vendor_id=data['vendor_id'],
            name=data['name'],
            quantity=data.get('quantity', 0),
            price_per_pc=data['price_per_pc']
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict_legacy(),
            'message': 'Product created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating product: {str(e)}'
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        data = request.get_json()
        
        # Validate category exists if provided
        if data.get('category_id'):
            category = Category.query.filter_by(category_id=data['category_id']).first()
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category not found'
                }), 400
        
        # Validate vendor exists if provided
        if data.get('vendor_id'):
            vendor = Vendor.query.filter_by(vendor_id=data['vendor_id']).first()
            if not vendor:
                return jsonify({
                    'success': False,
                    'message': 'Vendor not found'
                }), 400
        
        # Update fields
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'vendor_id' in data:
            product.vendor_id = data['vendor_id']
        if 'name' in data:
            product.name = data['name']
        if 'quantity' in data:
            product.quantity = data['quantity']
        if 'price_per_pc' in data:
            product.price_per_pc = data['price_per_pc']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict_legacy(),
            'message': 'Product updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating product: {str(e)}'
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting product: {str(e)}'
        }), 500

