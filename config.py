import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # 1. Security Keys
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-please-change")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-key-please-change")

    # 2. Database Connection Logic
    # Railway provides MYSQL_URL for MySQL databases
    # Priority: MYSQL_URL (Railway MySQL) -> DATABASE_URL (Railway Postgres) -> DATABASE_URI (Local)
    _db_url = (
        os.environ.get("MYSQL_URL")
        or os.environ.get("DATABASE_URL")
        or os.environ.get("DATABASE_URI")
        or os.environ.get("MYSQLHOST")  # Railway also sets MYSQLHOST, MYSQLUSER, etc.
    )

    # If Railway provides individual MySQL credentials, construct the URL
    if not _db_url and os.environ.get("MYSQLHOST"):
        mysql_user = os.environ.get("MYSQLUSER", "root")
        mysql_password = os.environ.get("MYSQLPASSWORD", "")
        mysql_host = os.environ.get("MYSQLHOST")
        mysql_port = os.environ.get("MYSQLPORT", "3306")
        mysql_database = os.environ.get("MYSQLDATABASE", "railway")
        _db_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

    # Fix for Postgres/MySQL prefixes if needed
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        if _db_url.startswith("mysql://"):
            _db_url = _db_url.replace("mysql://", "mysql+pymysql://", 1)

    # Set the final URI. If no cloud DB found, use local SQLite.
    SQLALCHEMY_DATABASE_URI = (
        _db_url or f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Other Settings
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    PROPAGATE_EXCEPTIONS = True

    # SQLAlchemy options (important for handling sleeping connections)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Test connections before using them
        "pool_recycle": 300,  # Recycle connections after 5 minutes
        "pool_size": 10,  # Connection pool size
        "max_overflow": 20,  # Max connections beyond pool_size
    }


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # In production, we force it to use the Parent Config's URI logic
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI


class DevelopmentConfig(Config):
    DEBUG = True
    # If no online DB is set, force SQLite for local development
    if not os.environ.get("MYSQL_URL") and not os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"
        )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Helper to load the correct class based on FLASK_ENV
def get_config(name=None):
    env = (name or os.getenv("FLASK_ENV", "production")).lower()
    if env in ["development", "dev"]:
        return DevelopmentConfig
    if env in ["testing", "test"]:
        return TestingConfig
    return ProductionConfig
