from src.models.user import db
from datetime import datetime

class Platform(db.Model):
    __tablename__ = 'platforms'
    
    platform_id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(255), nullable=False)
    
    # Relationships
    categories = db.relationship('Category', back_populates='platform')
    
    def to_dict(self):
        return {
            'platform_id': self.platform_id,
            'platform_name': self.platform_name
        }

