from src.models.user import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.platform_id'), nullable=False)
    category_name = db.Column(db.String(255), nullable=False)
    
    # Relationships
    platform = db.relationship('Platform', back_populates='categories')
    products = db.relationship('Product', back_populates='category')
    
    def to_dict(self):
        return {
            'category_id': self.category_id,
            'platform_id': self.platform_id,
            'category_name': self.category_name,
            'platform': self.platform.to_dict() if self.platform else None
        }
    
    # For backward compatibility with frontend
    def to_dict_legacy(self):
        return {
            'id': self.category_id,
            'name': self.category_name,
            'slug': self.category_name.lower().replace(' ', '-'),
            'description': f"Category for {self.platform.platform_name if self.platform else 'Unknown Platform'}",
            'parent_id': None,
            'is_active': True,
            'sort_order': 0,
            'children': [],
            'platform': self.platform.to_dict() if self.platform else None
        }

