"""
Order services with shipping charges calculation.
"""

from flask import current_app

from app.errors import ServiceError, ValidationError
from app.extensions import db
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.cart import Cart
from app.models.product import Product
from app.services.email_service import send_order_confirmation_email


def calculate_shipping_charges(subtotal: float) -> float:
    """
    Calculate shipping charges based on order subtotal.
    - Below threshold (₹2000): ₹49 shipping
    - Above threshold: Free shipping
    """
    threshold = current_app.config.get("SHIPPING_FREE_THRESHOLD", 2000)
    charge = current_app.config.get("SHIPPING_CHARGE", 49)
    
    if subtotal >= threshold:
        return 0.0
    return float(charge)


def create_order_from_cart(user_id: int, shipping_data: dict) -> dict:
    """
    Create an order from user's cart items.
    This creates the order in PENDING status awaiting payment.
    """
    # Get cart items
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        raise ValidationError("Cart is empty")

    # Calculate subtotal
    subtotal = 0.0
    order_items_data = []
    
    for cart_item in cart_items:
        if not cart_item.product:
            continue
        
        product = cart_item.product
        if product.stock < cart_item.quantity:
            raise ValidationError(
                f"Insufficient stock for {product.name}",
                details={"product_id": product.id, "available": product.stock}
            )
        
        item_total = float(product.price) * cart_item.quantity
        subtotal += item_total
        
        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "price": float(product.price),
        })

    if not order_items_data:
        raise ValidationError("No valid items in cart")

    # Calculate shipping
    shipping_charges = calculate_shipping_charges(subtotal)
    total_amount = subtotal + shipping_charges

    # Create order
    order = Order(
        user_id=user_id,
        subtotal=subtotal,
        shipping_charges=shipping_charges,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        customer_name=shipping_data.get("customer_name"),
        customer_email=shipping_data.get("customer_email"),
        customer_phone=shipping_data.get("customer_phone"),
        shipping_address_line1=shipping_data.get("address_line1"),
        shipping_address_line2=shipping_data.get("address_line2"),
        shipping_city=shipping_data.get("city"),
        shipping_state=shipping_data.get("state"),
        shipping_postal_code=shipping_data.get("postal_code"),
        shipping_country=shipping_data.get("country", "India"),
        notes=shipping_data.get("notes"),
    )
    
    db.session.add(order)
    
    try:
        db.session.flush()  # Get order ID
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to create order: {e}")

    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            price=item_data["price"],
        )
        db.session.add(order_item)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to create order items: {e}")

    return order.to_dict(include_items=True)


def confirm_order_payment(order_id: int, razorpay_payment_id: str) -> dict:
    """
    Confirm order after successful payment.
    - Updates order status to PAID
    - Deducts stock from products
    - Clears user's cart
    - Sends confirmation email
    """
    order = db.session.get(Order, order_id)
    if not order:
        raise ValidationError("Order not found")

    # Update order status
    order.status = OrderStatus.PAID
    order.payment_status = PaymentStatus.PAID
    order.razorpay_payment_id = razorpay_payment_id

    # Deduct stock
    for item in order.order_items:
        if item.product:
            item.product.stock -= item.quantity

    # Clear cart
    if order.user_id:
        Cart.query.filter_by(user_id=order.user_id).delete()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to confirm order: {e}")

    # Send confirmation email
    try:
        items = [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in order.order_items
        ]
        send_order_confirmation_email(order, items)
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")

    return order.to_dict(include_items=True)


def get_order_by_id(order_id: int, user_id: int = None) -> dict:
    """Get order by ID, optionally filtering by user."""
    order = db.session.get(Order, order_id)
    if not order:
        return None
    
    if user_id and order.user_id != user_id:
        return None
    
    return order.to_dict(include_items=True)


def get_orders_by_user(user_id: int) -> list:
    """Get all orders for a user."""
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return [order.to_dict() for order in orders]


def get_all_orders(status: str = None, page: int = 1, per_page: int = 20) -> dict:
    """Get all orders (admin only) with pagination."""
    query = Order.query.order_by(Order.created_at.desc())
    
    if status:
        try:
            status_enum = OrderStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        "orders": [order.to_dict() for order in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }


def update_order_status(order_id: int, new_status: str, tracking_info: dict = None) -> dict:
    """Update order status and optionally add tracking info (admin only)."""
    order = db.session.get(Order, order_id)
    if not order:
        raise ValidationError("Order not found")

    try:
        order.status = OrderStatus(new_status)
    except ValueError:
        raise ValidationError(f"Invalid status: {new_status}")

    if tracking_info:
        if "tracking_number" in tracking_info:
            order.tracking_number = tracking_info["tracking_number"]
        if "carrier" in tracking_info:
            order.carrier = tracking_info["carrier"]

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to update order: {e}")

    return order.to_dict()
