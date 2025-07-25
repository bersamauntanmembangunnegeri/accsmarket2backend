from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.vendor import Vendor

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/vendors', methods=['GET'])
def get_vendors():
    """Get all vendors"""
    try:
        vendors = Vendor.query.order_by(Vendor.vendor_name).all()
        
        vendors_data = []
        for vendor in vendors:
            vendors_data.append(vendor.to_dict())
        
        return jsonify({
            'success': True,
            'data': vendors_data,
            'message': 'Vendors retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving vendors: {str(e)}'
        }), 500

@vendors_bp.route('/vendors/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    """Get a specific vendor by ID"""
    try:
        vendor = Vendor.query.filter_by(vendor_id=vendor_id).first_or_404()
        return jsonify({
            'success': True,
            'data': vendor.to_dict(),
            'message': 'Vendor retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving vendor: {str(e)}'
        }), 500

@vendors_bp.route('/vendors', methods=['POST'])
def create_vendor():
    """Create a new vendor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('vendor_name'):
            return jsonify({
                'success': False,
                'message': 'Vendor name is required'
            }), 400
        
        vendor = Vendor(
            vendor_name=data['vendor_name'],
            contact_info=data.get('contact_info')
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': vendor.to_dict(),
            'message': 'Vendor created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating vendor: {str(e)}'
        }), 500

@vendors_bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update a vendor"""
    try:
        vendor = Vendor.query.filter_by(vendor_id=vendor_id).first_or_404()
        data = request.get_json()
        
        # Update fields
        if 'vendor_name' in data:
            vendor.vendor_name = data['vendor_name']
        if 'contact_info' in data:
            vendor.contact_info = data['contact_info']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': vendor.to_dict(),
            'message': 'Vendor updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating vendor: {str(e)}'
        }), 500

@vendors_bp.route('/vendors/<int:vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    """Delete a vendor"""
    try:
        vendor = Vendor.query.filter_by(vendor_id=vendor_id).first_or_404()
        
        # Check if vendor has products
        if vendor.products:
            return jsonify({
                'success': False,
                'message': 'Cannot delete vendor with products'
            }), 400
        
        db.session.delete(vendor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vendor deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting vendor: {str(e)}'
        }), 500

