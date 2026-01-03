"""
Unbound Flask extension objects.

Create the extension instances here (uninitialized) to avoid circular imports.
Initialize them in the application factory (app.create_app) using init_app.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

# Core DB + migration
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

# Auth
jwt: JWTManager = JWTManager()
bcrypt: Bcrypt = Bcrypt()

# Serialization / validation
ma: Marshmallow = Marshmallow()

# CORS
cors: CORS = CORS()

# Rate limiting
limiter: Limiter = Limiter(key_func=get_remote_address, headers_enabled=True)

# Email
mail: Mail = Mail()


def init_extensions(app) -> None:
    """Initialize all extensions with the Flask app."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    # CORS configuration
    cors_origins = app.config.get("CORS_ORIGINS", "*")
    cors.init_app(app, origins=cors_origins, supports_credentials=True)
    
    # Rate limiter
    limiter.init_app(app)
    
    # Email
    mail.init_app(app)
    
    app.logger.debug("Extensions initialized: db, migrate, jwt, bcrypt, ma, cors, limiter, mail")
