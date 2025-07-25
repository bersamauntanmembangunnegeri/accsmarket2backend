import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.category import Category
from src.models.subcategory import Subcategory
from src.models.product import Product
from src.models.order import Order, OrderItem
from src.models.settings import SiteSetting, WebsiteLayout

from src.routes.user import user_bp
from src.routes.categories import categories_bp
from src.routes.subcategories import subcategories_bp
from src.routes.products import products_bp
from src.routes.orders import orders_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes and origins
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')
app.register_blueprint(subcategories_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def seed_initial_data():
    """Seed initial data for testing"""
    with app.app_context():
        # Check if data already exists
        if Category.query.count() == 0:
            # Create sample categories
            facebook_cat = Category(name="Facebook Accounts", slug="facebook-accounts", description="High-quality Facebook accounts")
            instagram_cat = Category(name="Instagram Accounts", slug="instagram-accounts", description="Premium Instagram accounts")
            
            db.session.add(facebook_cat)
            db.session.add(instagram_cat)
            db.session.flush()
            
            # Create subcategories
            fb_softreg = Category(name="Facebook Softregs", slug="facebook-softregs", parent_id=facebook_cat.id)
            fb_friends = Category(name="Facebook With Friends", slug="facebook-with-friends", parent_id=facebook_cat.id)
            ig_softreg = Category(name="Instagram Softreg", slug="instagram-softreg", parent_id=instagram_cat.id)
            ig_aged = Category(name="Instagram Aged", slug="instagram-aged", parent_id=instagram_cat.id)
            
            db.session.add(fb_softreg)
            db.session.add(fb_friends)
            db.session.add(ig_softreg)
            db.session.add(ig_aged)
            db.session.flush()
            
            # Create sample products
            products = [
                Product(
                    category_id=fb_softreg.id,
                    title="FB Accounts | Verified by e-mail, there is no email in the set. Male or female. The account profiles may be empty or have limited entries such as photos and other information. 2FA included. Cookies are included. Accounts are registered in United Kingdom IP.",
                    description="High quality Facebook accounts verified by email",
                    price=0.278,
                    stock_quantity=345,
                    rating=4.6,
                    total_reviews=89,
                    account_type="Facebook Softreg",
                    is_active=True
                ),
                Product(
                    category_id=ig_softreg.id,
                    title="IG Accounts | Verified by email, email NOT included. Male or female. The profiles information is partially filled. 2FA included. UserAgent, cookies included. Registered from USA IP.",
                    description="Instagram soft registered accounts from USA",
                    price=0.183,
                    stock_quantity=99,
                    rating=4.9,
                    total_reviews=156,
                    account_type="Instagram Softreg",
                    is_active=True
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print("Initial data seeded successfully")

with app.app_context():
    db.create_all()
    seed_initial_data()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
