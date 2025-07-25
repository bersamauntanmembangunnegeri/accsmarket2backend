from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.product import Product
from src.models.category import Category

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id', type=int)
        is_featured = request.args.get('is_featured', type=bool)
        is_active = request.args.get('is_active', type=bool, default=True)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Build query
        query = Product.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if is_featured is not None:
            query = query.filter_by(is_featured=is_featured)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        # Order by featured first, then by rating, then by created_at
        query = query.order_by(Product.is_featured.desc(), Product.rating.desc(), Product.created_at.desc())
        
        # Paginate
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        products_data = []
        for product in products.items:
            products_data.append(product.to_dict())
        
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
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'data': product.to_dict(),
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
        if not data.get('title') or not data.get('price'):
            return jsonify({
                'success': False,
                'message': 'Title and price are required'
            }), 400
        
        # Validate category exists if provided
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category not found'
                }), 400
        
        product = Product(
            category_id=data.get('category_id'),
            seller_id=data.get('seller_id'),
            title=data['title'],
            description=data.get('description'),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            account_type=data.get('account_type'),
            account_details=data.get('account_details'),
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            rating=data.get('rating', 0.0),
            total_reviews=data.get('total_reviews', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
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
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Validate category exists if provided
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category not found'
                }), 400
        
        # Update fields
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'seller_id' in data:
            product.seller_id = data['seller_id']
        if 'title' in data:
            product.title = data['title']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'account_type' in data:
            product.account_type = data['account_type']
        if 'account_details' in data:
            product.account_details = data['account_details']
        if 'is_active' in data:
            product.is_active = data['is_active']
        if 'is_featured' in data:
            product.is_featured = data['is_featured']
        if 'rating' in data:
            product.rating = data['rating']
        if 'total_reviews' in data:
            product.total_reviews = data['total_reviews']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
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
        product = Product.query.get_or_404(product_id)
        
        # Check if product has orders
        if product.order_items:
            return jsonify({
                'success': False,
                'message': 'Cannot delete product with existing orders'
            }), 400
        
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

@products_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        products = Product.query.filter_by(is_featured=True, is_active=True).order_by(Product.rating.desc()).limit(10).all()
        
        products_data = []
        for product in products:
            products_data.append(product.to_dict())
        
        return jsonify({
            'success': True,
            'data': products_data,
            'message': 'Featured products retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving featured products: {str(e)}'
        }), 500

