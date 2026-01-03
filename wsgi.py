"""WSGI entry point for production deployment."""

import os
import sys
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

try:
    # Create the Flask application
    logger.info("Creating Flask application...")
    app = create_app()

    # Test database connection
    with app.app_context():
        from app.extensions import db

        try:
            # Try to execute a simple query to verify connection
            db.session.execute(db.text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            logger.info(
                f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Not set'}"
            )
        except Exception as db_error:
            logger.error(f"❌ Database connection failed: {str(db_error)}")
            logger.error("The app will start but database operations will fail.")
            logger.error(
                "Please check your DATABASE_URL or MYSQL_URL environment variable."
            )

    logger.info("🚀 WSGI app initialized successfully!")

except Exception as e:
    logger.error(f"❌ Failed to initialize application: {str(e)}")
    logger.error(f"Error type: {type(e).__name__}")
    import traceback

    logger.error(traceback.format_exc())
    raise
