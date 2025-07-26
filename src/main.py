import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.platform import Platform
from src.models.vendor import Vendor
from src.models.category import Category
from src.models.product import Product
from src.models.order import Order, OrderItem
from src.models.settings import SiteSetting, WebsiteLayout

from src.routes.user import user_bp
from src.routes.categories import categories_bp
from src.routes.products import products_bp
from src.routes.orders import orders_bp
from src.routes.admin import admin_bp
from src.routes.vendors import vendors_bp
from src.routes.platforms import platforms_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes and origins
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(vendors_bp, url_prefix='/api')
app.register_blueprint(platforms_bp, url_prefix='/api')

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
        if Platform.query.count() == 0:
            # Create sample platforms
            facebook_platform = Platform(platform_name="Facebook")
            instagram_platform = Platform(platform_name="Instagram")
            
            db.session.add(facebook_platform)
            db.session.add(instagram_platform)
            db.session.flush()
            
            # Create sample vendors
            vendor1 = Vendor(vendor_name="Premium Accounts Co", contact_info="contact@premiumaccs.com")
            vendor2 = Vendor(vendor_name="Social Media Hub", contact_info="info@socialmediahub.com")
            
            db.session.add(vendor1)
            db.session.add(vendor2)
            db.session.flush()
            
            # Create categories
            fb_category = Category(platform_id=facebook_platform.platform_id, category_name="Facebook Accounts")
            ig_category = Category(platform_id=instagram_platform.platform_id, category_name="Instagram Accounts")
            
            db.session.add(fb_category)
            db.session.add(ig_category)
            db.session.flush()
            
            # Create subcategories
            from src.models.subcategory import Subcategory
            
            # Facebook subcategories
            fb_softreg = Subcategory(name="Softreg", category_id=fb_category.category_id, icon="📧")
            fb_gmail = Subcategory(name="Gmail", category_id=fb_category.category_id, icon="📬")
            fb_aged = Subcategory(name="Aged", category_id=fb_category.category_id, icon="⏰")
            
            # Instagram subcategories  
            ig_softreg = Subcategory(name="Softreg", category_id=ig_category.category_id, icon="📧")
            ig_gmail = Subcategory(name="Gmail", category_id=ig_category.category_id, icon="📬")
            ig_aged = Subcategory(name="Aged", category_id=ig_category.category_id, icon="⏰")
            
            db.session.add_all([fb_softreg, fb_gmail, fb_aged, ig_softreg, ig_gmail, ig_aged])
            db.session.flush()
            
            # Create sample products
            products = [
                Product(
                    category_id=fb_category.category_id,
                    subcategory_id=fb_softreg.id,
                    vendor_id=vendor1.vendor_id,
                    name="FB Accounts | Verified by e-mail, there is no email in the set. Male or female. The account profiles may be empty or have limited entries such as photos and other information. 2FA included. Cookies are included. Accounts are registered in United Kingdom IP.",
                    quantity=345,
                    price_per_pc=0.278
                ),
                Product(
                    category_id=ig_category.category_id,
                    subcategory_id=ig_softreg.id,
                    vendor_id=vendor2.vendor_id,
                    name="IG Accounts | Verified by email, email NOT included. Male or female. The profiles information is partially filled. 2FA included. UserAgent, cookies included. Registered from USA IP.",
                    quantity=99,
                    price_per_pc=0.183
                ),
                Product(
                    category_id=fb_category.category_id,
                    subcategory_id=fb_gmail.id,
                    vendor_id=vendor1.vendor_id,
                    name="Gmail Accounts | Verified by SMS, Phone number not included in Profile Security method. There is an additional email address(without a password). Male or female. Registered from different countries IPs.",
                    quantity=115,
                    price_per_pc=0.278
                ),
                Product(
                    category_id=ig_category.category_id,
                    subcategory_id=ig_gmail.id,
                    vendor_id=vendor2.vendor_id,
                    name="Gmail Accounts | Accounts could be used in some services. The accounts are verified through SMS. There is an additional email address(without a password). Male or female. Registered from different countries IPs.",
                    quantity=404,
                    price_per_pc=0.183
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
