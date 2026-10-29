import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-in-production")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "instance" / "uploads"))
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Application settings
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "UTC")

    # Security cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False

    @staticmethod
    def get_database_uri() -> str:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Normalize legacy postgres:// to postgresql+psycopg://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
            elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
                db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
            return db_url
        # Default local PostgreSQL connection string
        return "postgresql+psycopg://app_user:replace-password@localhost:5432/job_tracker"


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    # If DATABASE_URL is explicitly provided use it; otherwise allow local sqlite dev fallback if postgres is absent
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'dev.db'}"
    )


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    # Use isolated in-memory or temporary SQLite database for automated tests
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    UPLOAD_FOLDER = str(BASE_DIR / "instance" / "test_uploads")
    SECRET_KEY = "test-secret-key-for-automated-tests"


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        uri = Config.get_database_uri()
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL environment variable must be set in production mode.")
        return uri


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
