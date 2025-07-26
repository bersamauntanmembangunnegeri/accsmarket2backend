from src.models.user import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=True)
    name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_pc = db.Column(db.Numeric(10, 2), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.vendor_id'), nullable=False)
    
    # Relationships
    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('Subcategory', backref='products')
    vendor = db.relationship('Vendor', back_populates='products')
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'category_id': self.category_id,
            'subcategory_id': self.subcategory_id,
            'name': self.name,
            'quantity': self.quantity,
            'price_per_pc': float(self.price_per_pc) if self.price_per_pc else 0.0,
            'vendor_id': self.vendor_id,
            'category': self.category.to_dict() if self.category else None,
            'subcategory': self.subcategory.to_dict() if self.subcategory else None,
            'vendor': self.vendor.to_dict() if self.vendor else None
        }
    
    # For backward compatibility with frontend
    def to_dict_legacy(self):
        return {
            'id': self.product_id,
            'category_id': self.category_id,
            'subcategory_id': self.subcategory_id,
            'title': self.name,
            'description': f"Product from {self.vendor.vendor_name if self.vendor else 'Unknown Vendor'}",
            'price': float(self.price_per_pc) if self.price_per_pc else 0.0,
            'stock_quantity': self.quantity,
            'account_type': self.category.category_name if self.category else 'Unknown',
            'is_active': True,
            'is_featured': False,
            'rating': 4.5,  # Default rating
            'total_reviews': 0,
            'category': self.category.to_dict_legacy() if self.category else None,
            'subcategory': self.subcategory.to_dict() if self.subcategory else None,
            'vendor': self.vendor.to_dict() if self.vendor else None
        }

