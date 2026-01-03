"""
Application factory.
"""

from flask import Flask
from .extensions import db, migrate, bcrypt, jwt, ma, cors, limiter, mail
from .routes import register_blueprints
from .errors import register_error_handlers


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    # 1. LOAD CONFIGURATION
    if config_object:
        app.config.from_object(config_object)
    else:
        from config import get_config
        app.config.from_object(get_config())

    # 2. INITIALIZE EXTENSIONS
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, origins="*", supports_credentials=True)
    limiter.init_app(app)
    mail.init_app(app)

    # 3. LOAD MODELS
    from app import models

    # 4. REGISTER BLUEPRINTS
    register_blueprints(app)

    # 5. REGISTER ERROR HANDLERS
    register_error_handlers(app)

    # 6. HEALTH CHECK ROUTES
    @app.route("/")
    def health_check():
        return {
            "status": "success",
            "message": "KOMPLYTE Backend is Running!",
            "service": "KOMPLYTE E-commerce API",
            "version": "2.0.0",
        }, 200

    @app.route("/health")
    def health():
        """Health check endpoint for Railway."""
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return {
            "status": "healthy",
            "database": db_status,
            "service": "KOMPLYTE API",
        }, 200

    @app.route("/ping")
    def ping():
        """Simple ping endpoint."""
        return {"status": "pong"}, 200

    return app
