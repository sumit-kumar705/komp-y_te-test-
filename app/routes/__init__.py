"""
Blueprint registration for all routes.
"""


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    
    # Auth routes
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    
    # Product routes (GET public, POST/PUT/DELETE admin)
    from app.routes.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix="/api/v1/products")
    
    # Category routes (GET public, POST/PUT/DELETE admin)
    from app.routes.category_routes import category_bp
    app.register_blueprint(category_bp, url_prefix="/api/v1/categories")
    
    # Cart routes (all require auth)
    from app.routes.cart_routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix="/api/v1/cart")
    
    # Order routes (all require auth)
    from app.routes.order_routes import order_bp
    app.register_blueprint(order_bp, url_prefix="/api/v1/orders")
    
    # Payment routes (Razorpay integration)
    from app.routes.payment_routes import payment_bp
    app.register_blueprint(payment_bp, url_prefix="/api/v1/payments")
    
    # Booking routes (consultation scheduling)
    from app.routes.booking_routes import booking_bp
    app.register_blueprint(booking_bp, url_prefix="/api/v1/bookings")
    
    # Admin routes (all require admin role)
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    
    # User routes
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/v1/users")
    
    # Config routes (public info endpoints)
    from app.routes.config_routes import config_bp
    app.register_blueprint(config_bp, url_prefix="/api/v1/config")
