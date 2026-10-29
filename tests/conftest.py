import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db_session(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        # Clear tables
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
        yield _db.session
        _db.session.rollback()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create and return a sample verified test user."""
    user = User(
        full_name="Alex Developer",
        email="alex@example.com",
        timezone="UTC",
    )
    user.set_password("SecurePassword123!")
    db_session.add(user)
    db_session.commit()
    return user
