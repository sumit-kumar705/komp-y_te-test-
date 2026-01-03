"""
Product services.
"""

from app.extensions import db
from app.models.product import Product
from app.utils.response import format_model


def get_products(category_id: int = None, active_only: bool = True) -> list:
    """Get all products with optional filters."""
    query = Product.query
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.created_at.desc()).all()
    return [format_model(p) for p in products]


def get_featured_products() -> list:
    """Get featured products."""
    products = Product.query.filter_by(is_active=True, is_featured=True).all()
    return [format_model(p) for p in products]


def search_products(query: str) -> list:
    """Search products by name or description."""
    search_term = f"%{query}%"
    products = Product.query.filter(
        Product.is_active == True,
        (Product.name.ilike(search_term) | Product.description.ilike(search_term))
    ).all()
    return [format_model(p) for p in products]


def get_product_by_id(product_id: int) -> dict:
    """Get product by ID."""
    product = db.session.get(Product, product_id)
    return format_model(product) if product else None


def create_product(data: dict) -> dict:
    """Create a new product."""
    try:
        product = Product(
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price"),
            stock=data.get("stock", 0),
            category_id=data.get("category_id"),
            main_image=data.get("main_image"),
            images=data.get("images"),
            ingredients=data.get("ingredients"),
            benefits=data.get("benefits"),
            nutrition_info=data.get("nutrition_info"),
            usage_instructions=data.get("usage_instructions"),
            weight=data.get("weight"),
            sku=data.get("sku"),
            is_active=data.get("is_active", True),
            is_featured=data.get("is_featured", False),
        )
        db.session.add(product)
        db.session.commit()
        return format_model(product)

    except Exception as e:
        db.session.rollback()
        raise e


def update_product(product_id: int, data: dict) -> dict:
    """Update a product."""
    product = db.session.get(Product, product_id)
    if not product:
        return None

    try:
        # Update all provided fields
        updatable_fields = [
            "name", "description", "price", "stock", "category_id",
            "main_image", "images", "ingredients", "benefits",
            "nutrition_info", "usage_instructions", "weight", "sku",
            "is_active", "is_featured"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])

        db.session.commit()
        return format_model(product)

    except Exception as e:
        db.session.rollback()
        raise e


def delete_product(product_id: int) -> bool:
    """Delete a product."""
    product = db.session.get(Product, product_id)
    if not product:
        return False

    try:
        db.session.delete(product)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        raise e
