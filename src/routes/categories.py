from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.category import Category
from src.models.platform import Platform

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.order_by(Category.category_name).all()
        
        categories_data = []
        for category in categories:
            categories_data.append(category.to_dict_legacy())
        
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
        category = Category.query.filter_by(category_id=category_id).first_or_404()
        return jsonify({
            'success': True,
            'data': category.to_dict_legacy(),
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
        if not data.get('category_name') or not data.get('platform_id'):
            return jsonify({
                'success': False,
                'message': 'Category name and platform ID are required'
            }), 400
        
        # Validate platform exists
        platform = Platform.query.filter_by(platform_id=data['platform_id']).first()
        if not platform:
            return jsonify({
                'success': False,
                'message': 'Platform not found'
            }), 400
        
        category = Category(
            platform_id=data['platform_id'],
            category_name=data['category_name']
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': category.to_dict_legacy(),
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
        category = Category.query.filter_by(category_id=category_id).first_or_404()
        data = request.get_json()
        
        # Validate platform exists if provided
        if data.get('platform_id'):
            platform = Platform.query.filter_by(platform_id=data['platform_id']).first()
            if not platform:
                return jsonify({
                    'success': False,
                    'message': 'Platform not found'
                }), 400
        
        # Update fields
        if 'platform_id' in data:
            category.platform_id = data['platform_id']
        if 'category_name' in data:
            category.category_name = data['category_name']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': category.to_dict_legacy(),
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
        category = Category.query.filter_by(category_id=category_id).first_or_404()
        
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

