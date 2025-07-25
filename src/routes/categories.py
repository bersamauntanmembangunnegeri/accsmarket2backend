from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.category import Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories with their children"""
    try:
        # Get only parent categories (no parent_id)
        parent_categories = Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.sort_order, Category.name).all()
        
        categories_data = []
        for category in parent_categories:
            categories_data.append(category.to_dict())
        
        return jsonify({
            'success': True,
            'data': categories_data,
            'message': 'Categories retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving categories: {str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category by ID"""
    try:
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': 'Category retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving category: {str(e)}'
        }), 500

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('slug'):
            return jsonify({
                'success': False,
                'message': 'Name and slug are required'
            }), 400
        
        # Check if slug already exists
        existing_category = Category.query.filter_by(slug=data['slug']).first()
        if existing_category:
            return jsonify({
                'success': False,
                'message': 'Category with this slug already exists'
            }), 400
        
        category = Category(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': 'Category created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating category: {str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        # Check if slug already exists (excluding current category)
        if data.get('slug') and data['slug'] != category.slug:
            existing_category = Category.query.filter_by(slug=data['slug']).first()
            if existing_category:
                return jsonify({
                    'success': False,
                    'message': 'Category with this slug already exists'
                }), 400
        
        # Update fields
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            category.slug = data['slug']
        if 'description' in data:
            category.description = data['description']
        if 'parent_id' in data:
            category.parent_id = data['parent_id']
        if 'is_active' in data:
            category.is_active = data['is_active']
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': 'Category updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating category: {str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category has children
        if category.children:
            return jsonify({
                'success': False,
                'message': 'Cannot delete category with subcategories'
            }), 400
        
        # Check if category has products
        if category.products:
            return jsonify({
                'success': False,
                'message': 'Cannot delete category with products'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Category deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting category: {str(e)}'
        }), 500

