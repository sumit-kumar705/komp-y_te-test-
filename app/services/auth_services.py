from app.errors import ServiceError
from app.extensions import db, bcrypt
from app.models.user import User
from app.utils.jwt_utils import generate_access_token


def create_user(name, email, password, role="customer"):
    """Create a new user."""
    if User.query.filter(User.email == email).first():
        raise ValueError("User with this email already exists")

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=name, email=email, password_hash=password_hash, role=role)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return user


def authenticate_user(email, password):
    """Authenticate user and return user with JWT token."""
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        token = generate_access_token(str(user.id))
        return user, token

    return None, None


def get_user_by_id(user_id):
    """Get user by ID and return as dict."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.session.get(User, user_id)

    if user:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
            "role": user.role,
            "phone": user.phone,
            "address_line1": user.address_line1,
            "city": user.city,
            "state": user.state,
            "postal_code": user.postal_code,
            "country": user.country,
        }

    return None


def update_user_profile(user_id, data):
    """Update user profile."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.session.get(User, user_id)
    if not user:
        return None

    # Update allowed fields
    allowed_fields = [
        "username", "phone", "address_line1", "address_line2",
        "city", "state", "postal_code", "country"
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return user.to_dict()


def create_admin_user(name, email, password):
    """Create an admin user."""
    return create_user(name, email, password, role="admin")
