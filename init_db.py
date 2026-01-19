"""
Simple database initialization script for Railway deployment.
This creates all tables without using migrations.
Run this ONCE after first deployment: railway run python init_db.py
"""

import os
import sys


def init_database():
    """Initialize database tables."""
    try:
        from app import create_app
        from app.extensions import db
        
        # Create app instance
        app = create_app()
        
        with app.app_context():
            print("=" * 70)
            print("🔧 KOMPLYTE Database Initialization")
            print("=" * 70)
            print()
            
            # Check database connection
            print("1. Testing database connection...")
            try:
                db.session.execute(db.text("SELECT 1"))
                print("   ✅ Database connection successful!")
                print(f"   Database: {app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Local SQLite'}")
            except Exception as e:
                print(f"   ❌ Database connection failed: {e}")
                return False
            
            print()
            print("2. Creating all database tables...")
            try:
                # Import all models to ensure they're registered
                from app import models
                
                # Create all tables
                db.create_all()
                print("   ✅ All tables created successfully!")
                
                # List created tables
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"   Created {len(tables)} tables:")
                for table in sorted(tables):
                    print(f"      - {table}")
                
            except Exception as e:
                print(f"   ❌ Table creation failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            print()
            print("=" * 70)
            print("🎉 Database initialization completed successfully!")
            print("=" * 70)
            print()
            print("Next steps:")
            print("1. Create an admin user: railway run python scripts/admin_setup.py")
            print("2. Test your API endpoints")
            print()
            
            return True
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
