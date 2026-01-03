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

    # Create all database tables
    with app.app_context():
        from app.extensions import db

        db.create_all()
        print("✓ Database tables created successfully!")

    # Run the application
    print("=" * 50)
    print("🚀 Starting Flask Development Server")
    print("=" * 50)
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
