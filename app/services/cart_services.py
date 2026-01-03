"""
Cart services.
"""

from app.errors import ServiceError, ValidationError
from app.extensions import db
from app.models.cart import Cart
from app.models.product import Product


def get_user_cart(user_id: int) -> dict:
    """Get user's cart with items and totals."""
    items = Cart.query.filter_by(user_id=user_id).all()
    
    cart_items = []
    subtotal = 0.0
    
    for item in items:
        if item.product:
            item_total = float(item.product.price) * item.quantity
            subtotal += item_total
            cart_items.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": float(item.product.price),
                    "main_image": item.product.main_image,
                    "stock": item.product.stock,
                },
                "line_total": item_total,
            })
    
    # Calculate shipping based on config
    from flask import current_app
    threshold = current_app.config.get("SHIPPING_FREE_THRESHOLD", 2000)
    charge = current_app.config.get("SHIPPING_CHARGE", 49)
    shipping = 0.0 if subtotal >= threshold else float(charge)
    
    return {
        "items": cart_items,
        "item_count": len(cart_items),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": subtotal + shipping,
    }


def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> dict:
    """Add item to cart or update quantity if exists."""
    # Verify product exists and has stock
    product = db.session.get(Product, product_id)
    if not product:
        raise ValidationError("Product not found")
    
    if not product.is_active:
        raise ValidationError("Product is not available")
    
    if product.stock < quantity:
        raise ValidationError(f"Only {product.stock} items available")

    # Check if item already in cart
    existing_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing_item:
        new_quantity = existing_item.quantity + quantity
        if product.stock < new_quantity:
            raise ValidationError(f"Only {product.stock} items available")
        existing_item.quantity = new_quantity
    else:
        existing_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(existing_item)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to add to cart: {e}")

    return {
        "id": existing_item.id,
        "product_id": existing_item.product_id,
        "quantity": existing_item.quantity,
    }


def update_cart_item(user_id: int, product_id: int, quantity: int) -> dict:
    """Update cart item quantity."""
    item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return None

    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        db.session.delete(item)
        db.session.commit()
        return {"removed": True}

    # Check stock
    if item.product and item.product.stock < quantity:
        raise ValidationError(f"Only {item.product.stock} items available")

    item.quantity = quantity
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to update cart: {e}")

    return {
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
    }


def remove_from_cart(user_id: int, product_id: int) -> bool:
    """Remove item from cart."""
    item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return False

    db.session.delete(item)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to remove from cart: {e}")

    return True


def clear_cart(user_id: int) -> bool:
    """Clear all items from user's cart."""
    Cart.query.filter_by(user_id=user_id).delete()
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to clear cart: {e}")

    return True
