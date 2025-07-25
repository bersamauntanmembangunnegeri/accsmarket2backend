from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.platform import Platform

platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get all platforms"""
    try:
        platforms = Platform.query.order_by(Platform.platform_name).all()
        
        platforms_data = []
        for platform in platforms:
            platforms_data.append(platform.to_dict())
        
        return jsonify({
            'success': True,
            'data': platforms_data,
            'message': 'Platforms retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving platforms: {str(e)}'
        }), 500

@platforms_bp.route('/platforms/<int:platform_id>', methods=['GET'])
def get_platform(platform_id):
    """Get a specific platform by ID"""
    try:
        platform = Platform.query.filter_by(platform_id=platform_id).first_or_404()
        return jsonify({
            'success': True,
            'data': platform.to_dict(),
            'message': 'Platform retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving platform: {str(e)}'
        }), 500

@platforms_bp.route('/platforms', methods=['POST'])
def create_platform():
    """Create a new platform"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('platform_name'):
            return jsonify({
                'success': False,
                'message': 'Platform name is required'
            }), 400
        
        platform = Platform(
            platform_name=data['platform_name']
        )
        
        db.session.add(platform)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': platform.to_dict(),
            'message': 'Platform created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating platform: {str(e)}'
        }), 500

@platforms_bp.route('/platforms/<int:platform_id>', methods=['PUT'])
def update_platform(platform_id):
    """Update a platform"""
    try:
        platform = Platform.query.filter_by(platform_id=platform_id).first_or_404()
        data = request.get_json()
        
        # Update fields
        if 'platform_name' in data:
            platform.platform_name = data['platform_name']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': platform.to_dict(),
            'message': 'Platform updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating platform: {str(e)}'
        }), 500

@platforms_bp.route('/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    """Delete a platform"""
    try:
        platform = Platform.query.filter_by(platform_id=platform_id).first_or_404()
        
        # Check if platform has categories
        if platform.categories:
            return jsonify({
                'success': False,
                'message': 'Cannot delete platform with categories'
            }), 400
        
        db.session.delete(platform)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Platform deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting platform: {str(e)}'
        }), 500

