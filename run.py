"""
Run this script to start your Flask application locally
"""

import os
from pathlib import Path

# Ensure instance folder exists
instance_path = Path(__file__).parent / "instance"
instance_path.mkdir(exist_ok=True)

# Set environment variables if not already set
if not os.environ.get("FLASK_ENV"):
    os.environ["FLASK_ENV"] = "development"

if __name__ == "__main__":
    from app import create_app

    app = create_app()

    # Database tables should be created via migrations (flask db upgrade)
    # Not using db.create_all() to avoid conflicts with Alembic migrations
    with app.app_context():
        from app.extensions import db

        # Just verify connection
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✓ Database connection verified!")
        except Exception as e:
            print(f"⚠️  Database connection warning: {e}")
            print("Run 'python -m flask db upgrade' to create tables")

    # Run the application
    print("=" * 50)
    print("🚀 Starting Flask Development Server")
    print("=" * 50)
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
