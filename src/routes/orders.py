from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.order import Order, OrderItem
from src.models.product import Product

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        payment_status = request.args.get('payment_status')
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Build query
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        if payment_status:
            query = query.filter_by(payment_status=payment_status)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # Order by created_at desc
        query = query.order_by(Order.created_at.desc())
        
        # Paginate
        orders = query.paginate(page=page, per_page=per_page, error_out=False)
        
        orders_data = []
        for order in orders.items:
            orders_data.append(order.to_dict())
        
        return jsonify({
            'success': True,
            'data': orders_data,
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            },
            'message': 'Orders retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving orders: {str(e)}'
        }), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': 'Order retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving order: {str(e)}'
        }), 500

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_email') or not data.get('order_items'):
            return jsonify({
                'success': False,
                'message': 'Customer email and order items are required'
            }), 400
        
        # Calculate total amount
        total_amount = 0
        order_items_data = data['order_items']
        
        # Validate products and calculate total
        for item_data in order_items_data:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({
                    'success': False,
                    'message': f'Product with ID {item_data["product_id"]} not found'
                }), 400
            
            quantity = item_data.get('quantity', 1)
            unit_price = float(product.price)
            item_total = unit_price * quantity
            total_amount += item_total
        
        # Create order
        order = Order(
            user_id=data.get('user_id'),
            customer_email=data['customer_email'],
            customer_name=data.get('customer_name'),
            total_amount=total_amount,
            status=data.get('status', 'pending'),
            payment_status=data.get('payment_status', 'pending'),
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item_data in order_items_data:
            product = Product.query.get(item_data['product_id'])
            quantity = item_data.get('quantity', 1)
            unit_price = float(product.price)
            item_total = unit_price * quantity
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': 'Order created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating order: {str(e)}'
        }), 500

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an order"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Update fields
        if 'customer_email' in data:
            order.customer_email = data['customer_email']
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        if 'status' in data:
            order.status = data['status']
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
        if 'payment_method' in data:
            order.payment_method = data['payment_method']
        if 'notes' in data:
            order.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': 'Order updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating order: {str(e)}'
        }), 500

@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order"""
    try:
        order = Order.query.get_or_404(order_id)
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting order: {str(e)}'
        }), 500

@orders_bp.route('/orders/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics"""
    try:
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'total_revenue': float(total_revenue)
            },
            'message': 'Order statistics retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving order statistics: {str(e)}'
        }), 500

