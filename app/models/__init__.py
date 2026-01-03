# Models package initialization
from flask_sqlalchemy import SQLAlchemy

# Do NOT import models yet — SQLAlchemy must initialize first
# db = SQLAlchemy() is in extensions.py

from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.blog import Blog
from app.models.booking import Booking, BookingStatus
from app.models.faq import FAQ
from app.models.contact import Contact, InquiryStatus
from app.models.newsletter import Newsletter
from app.models.review import Review
from app.models.team import TeamMember
