from app.models.user import User


def test_app_creation_and_config(app):
    """Test that application factory sets up testing configuration correctly."""
    assert app.testing is True
    assert app.config["WTF_CSRF_ENABLED"] is False


def test_landing_page(client):
    """Test that public landing page loads with required headline."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Track every job application in one place." in response.data
    assert b"Application Tracker" in response.data
    assert b"Create account" in response.data


def test_api_health(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "automated-job-application-tracker"


def test_404_error_page(client):
    """Test that a nonexistent page returns 404 with custom error page."""
    response = client.get("/nonexistent-endpoint-xyz")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_user_password_hashing(db_session):
    """Test secure password hashing on the User model."""
    user = User(
        full_name="Morgan Reed",
        email="morgan@example.com",
    )
    user.set_password("MySecurePass123!")
    db_session.add(user)
    db_session.commit()

    assert user.password_hash != "MySecurePass123!"
    assert user.check_password("MySecurePass123!") is True
    assert user.check_password("WrongPassword") is False
