from src.models.user import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.Text)
    
    # Relationships
    products = db.relationship('Product', back_populates='vendor')
    
    def to_dict(self):
        return {
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor_name,
            'contact_info': self.contact_info
        }

