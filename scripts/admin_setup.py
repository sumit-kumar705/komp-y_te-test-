#!/usr/bin/env python
"""
Admin Setup Script

Run this script to create or reset the admin account.
Usage: python scripts/admin_setup.py

Environment variables (or will prompt):
- ADMIN_EMAIL: Admin email address
- ADMIN_PASSWORD: Admin password
- ADMIN_NAME: Admin username
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.services.auth_services import create_admin_user


def setup_admin():
    app = create_app()
    
    with app.app_context():
        # Get admin credentials
        admin_email = os.environ.get("ADMIN_EMAIL") or input("Admin email: ").strip()
        admin_password = os.environ.get("ADMIN_PASSWORD") or input("Admin password: ").strip()
        admin_name = os.environ.get("ADMIN_NAME") or input("Admin name (default: Admin): ").strip() or "Admin"
        
        if not admin_email or not admin_password:
            print("Error: Email and password are required!")
            sys.exit(1)
        
        # Check if admin exists
        existing = User.query.filter_by(email=admin_email).first()
        
        if existing:
            if existing.role == "admin":
                print(f"Admin account already exists: {admin_email}")
                update = input("Update password? (y/N): ").strip().lower()
                if update == "y":
                    existing.set_password(admin_password)
                    db.session.commit()
                    print("✓ Admin password updated!")
            else:
                # Upgrade to admin
                existing.role = "admin"
                existing.set_password(admin_password)
                db.session.commit()
                print(f"✓ Upgraded {admin_email} to admin!")
        else:
            # Create new admin
            try:
                admin = create_admin_user(admin_name, admin_email, admin_password)
                print(f"✓ Admin account created: {admin.email}")
            except Exception as e:
                print(f"Error creating admin: {e}")
                sys.exit(1)
        
        print("\n" + "=" * 50)
        print("Admin Setup Complete!")
        print("=" * 50)
        print(f"Email: {admin_email}")
        print("You can now login at /api/v1/auth/login")


if __name__ == "__main__":
    setup_admin()
