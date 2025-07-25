from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.subcategory import Subcategory
from src.models.category import Category

subcategories_bp = Blueprint('subcategories', __name__)

@subcategories_bp.route('/subcategories', methods=['GET'])
def get_subcategories():
    """Get all subcategories with optional filtering by category"""
    try:
        category_id = request.args.get('category_id', type=int)
        
        query = Subcategory.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        subcategories = query.order_by(Subcategory.name).all()
        
        subcategories_data = []
        for subcategory in subcategories:
            subcategories_data.append(subcategory.to_dict())
        
        return jsonify({
            'success': True,
            'data': subcategories_data,
            'message': 'Subcategories retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving subcategories: {str(e)}'
        }), 500

@subcategories_bp.route('/subcategories/<int:subcategory_id>', methods=['GET'])
def get_subcategory(subcategory_id):
    """Get a specific subcategory by ID"""
    try:
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        return jsonify({
            'success': True,
            'data': subcategory.to_dict(),
            'message': 'Subcategory retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving subcategory: {str(e)}'
        }), 500

@subcategories_bp.route('/subcategories', methods=['POST'])
def create_subcategory():
    """Create a new subcategory"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Name is required'
            }), 400
        
        # Validate category exists if provided
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category not found'
                }), 400
        
        # Check if subcategory with same name exists in the same category
        existing_subcategory = Subcategory.query.filter_by(
            name=data['name'], 
            category_id=data.get('category_id')
        ).first()
        if existing_subcategory:
            return jsonify({
                'success': False,
                'message': 'Subcategory with this name already exists in this category'
            }), 400
        
        subcategory = Subcategory(
            name=data['name'],
            category_id=data.get('category_id'),
            icon=data.get('icon'),
            product_count=data.get('product_count', 0)
        )
        
        db.session.add(subcategory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': subcategory.to_dict(),
            'message': 'Subcategory created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating subcategory: {str(e)}'
        }), 500

@subcategories_bp.route('/subcategories/<int:subcategory_id>', methods=['PUT'])
def update_subcategory(subcategory_id):
    """Update a subcategory"""
    try:
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        data = request.get_json()
        
        # Validate category exists if provided
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category not found'
                }), 400
        
        # Check if subcategory with same name exists in the same category (excluding current)
        if data.get('name') and (data['name'] != subcategory.name or data.get('category_id') != subcategory.category_id):
            existing_subcategory = Subcategory.query.filter_by(
                name=data['name'], 
                category_id=data.get('category_id', subcategory.category_id)
            ).filter(Subcategory.id != subcategory_id).first()
            if existing_subcategory:
                return jsonify({
                    'success': False,
                    'message': 'Subcategory with this name already exists in this category'
                }), 400
        
        # Update fields
        if 'name' in data:
            subcategory.name = data['name']
        if 'category_id' in data:
            subcategory.category_id = data['category_id']
        if 'icon' in data:
            subcategory.icon = data['icon']
        if 'product_count' in data:
            subcategory.product_count = data['product_count']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': subcategory.to_dict(),
            'message': 'Subcategory updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating subcategory: {str(e)}'
        }), 500

@subcategories_bp.route('/subcategories/<int:subcategory_id>', methods=['DELETE'])
def delete_subcategory(subcategory_id):
    """Delete a subcategory"""
    try:
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        
        db.session.delete(subcategory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subcategory deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting subcategory: {str(e)}'
        }), 500

