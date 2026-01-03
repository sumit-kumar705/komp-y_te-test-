"""
Email service for sending order confirmations and notifications.
"""

from flask import current_app, render_template_string
from flask_mail import Message

from app.extensions import mail


# HTML Email Templates
ORDER_CONFIRMATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .order-details { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .total { font-size: 1.2em; font-weight: bold; color: #667eea; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Order Confirmed!</h1>
            <p>Thank you for your order, {{ customer_name }}!</p>
        </div>
        <div class="content">
            <h2>Order #{{ order_id }}</h2>
            <p>We've received your order and payment. Your order is being processed!</p>
            
            <div class="order-details">
                <h3>Order Summary</h3>
                {% for item in items %}
                <div class="item">
                    <span>{{ item.product_name }} x {{ item.quantity }}</span>
                    <span>₹{{ "%.2f"|format(item.price * item.quantity) }}</span>
                </div>
                {% endfor %}
                <div class="item">
                    <span>Subtotal</span>
                    <span>₹{{ "%.2f"|format(subtotal) }}</span>
                </div>
                <div class="item">
                    <span>Shipping</span>
                    <span>{% if shipping_charges == 0 %}FREE{% else %}₹{{ "%.2f"|format(shipping_charges) }}{% endif %}</span>
                </div>
                <div class="item total">
                    <span>Total</span>
                    <span>₹{{ "%.2f"|format(total_amount) }}</span>
                </div>
            </div>
            
            <div class="order-details">
                <h3>Shipping Address</h3>
                <p>
                    {{ shipping_address_line1 }}<br>
                    {% if shipping_address_line2 %}{{ shipping_address_line2 }}<br>{% endif %}
                    {{ shipping_city }}, {{ shipping_state }} {{ shipping_postal_code }}<br>
                    {{ shipping_country }}
                </p>
            </div>
            
            <p>We'll notify you when your order ships!</p>
            
            <h3>Need Help?</h3>
            <p>For returns and refunds, please reach out to us on WhatsApp: <a href="https://wa.me/{{ admin_whatsapp }}">{{ admin_whatsapp }}</a></p>
            <p>Email: <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
        </div>
        <div class="footer">
            <p>© {{ year }} {{ company_name }}. All rights reserved.</p>
            <p>Support your Gut, Support your Health - anywhere, anytime.</p>
        </div>
    </div>
</body>
</html>
"""

PAYMENT_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .amount { font-size: 2em; font-weight: bold; color: #11998e; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Payment Successful!</h1>
        </div>
        <div class="content">
            <p>Hi {{ customer_name }},</p>
            <p>Your payment has been successfully processed.</p>
            
            <p class="amount">₹{{ "%.2f"|format(amount) }}</p>
            <p>Payment ID: {{ payment_id }}</p>
            <p>Order ID: #{{ order_id }}</p>
            
            <p>Your order is now confirmed and will be shipped soon!</p>
        </div>
        <div class="footer">
            <p>© {{ year }} {{ company_name }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def send_order_confirmation_email(order, items):
    """Send order confirmation email to customer."""
    try:
        if not order.customer_email:
            current_app.logger.warning(f"No email for order {order.id}")
            return False

        from datetime import datetime
        
        html_content = render_template_string(
            ORDER_CONFIRMATION_TEMPLATE,
            order_id=order.id,
            customer_name=order.customer_name or "Valued Customer",
            items=items,
            subtotal=float(order.subtotal) if order.subtotal else 0,
            shipping_charges=float(order.shipping_charges) if order.shipping_charges else 0,
            total_amount=float(order.total_amount) if order.total_amount else 0,
            shipping_address_line1=order.shipping_address_line1 or "",
            shipping_address_line2=order.shipping_address_line2 or "",
            shipping_city=order.shipping_city or "",
            shipping_state=order.shipping_state or "",
            shipping_postal_code=order.shipping_postal_code or "",
            shipping_country=order.shipping_country or "India",
            admin_whatsapp=current_app.config.get("ADMIN_WHATSAPP", "918149550229"),
            support_email=current_app.config.get("SUPPORT_EMAIL", "support@komplyte.com"),
            company_name=current_app.config.get("COMPANY_NAME", "KOMPLYTE"),
            year=datetime.now().year,
        )

        msg = Message(
            subject=f"Order Confirmed! #{order.id} - {current_app.config.get('COMPANY_NAME', 'KOMPLYTE')}",
            recipients=[order.customer_email],
            html=html_content,
        )
        
        mail.send(msg)
        current_app.logger.info(f"Order confirmation email sent for order {order.id}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send order confirmation email: {e}")
        return False


def send_payment_success_email(order, payment):
    """Send payment success email to customer."""
    try:
        if not order.customer_email:
            current_app.logger.warning(f"No email for order {order.id}")
            return False

        from datetime import datetime
        
        html_content = render_template_string(
            PAYMENT_SUCCESS_TEMPLATE,
            customer_name=order.customer_name or "Valued Customer",
            amount=float(payment.amount) if payment.amount else 0,
            payment_id=payment.razorpay_payment_id or payment.id,
            order_id=order.id,
            company_name=current_app.config.get("COMPANY_NAME", "KOMPLYTE"),
            year=datetime.now().year,
        )

        msg = Message(
            subject=f"Payment Successful - {current_app.config.get('COMPANY_NAME', 'KOMPLYTE')}",
            recipients=[order.customer_email],
            html=html_content,
        )
        
        mail.send(msg)
        current_app.logger.info(f"Payment success email sent for order {order.id}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send payment success email: {e}")
        return False
