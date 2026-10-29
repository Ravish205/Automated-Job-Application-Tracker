from app.extensions import db
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


def test_successful_registration(client, db_session):
    """Test registering a new user creates a database record and logs in."""
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Jane Candidate",
            "email": "jane@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully" in response.data
    assert b"Jane Candidate" in response.data

    user = db_session.execute(
        db.select(User).filter_by(email="jane@example.com")
    ).scalar_one_or_none()
    assert user is not None
    assert user.full_name == "Jane Candidate"
    assert user.check_password("SecurePassword123!") is True


def test_duplicate_registration_prevented(client, test_user):
    """Test that registering an existing email is rejected and prevents duplicate creation."""
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Duplicate User",
            "email": test_user.email,
            "password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!",
        },
    )
    assert response.status_code == 400
    assert b"An account with this email address already exists." in response.data


def test_registration_validation_errors(client):
    """Test validation errors for short password and password mismatch."""
    # Short password
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Short Pass",
            "email": "short@example.com",
            "password": "short",
            "confirm_password": "short",
        },
    )
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long." in response.data

    # Mismatched passwords
    response_mismatch = client.post(
        "/auth/register",
        data={
            "full_name": "Mismatch Pass",
            "email": "mismatch@example.com",
            "password": "Password12345!",
            "confirm_password": "DifferentPassword12345!",
        },
    )
    assert response_mismatch.status_code == 200
    assert b"Passwords must match." in response_mismatch.data


def test_successful_login_and_logout(client, test_user):
    """Test login with valid credentials and subsequent logout."""
    response = client.post(
        "/auth/login",
        data={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Signed in successfully." in response.data
    assert b"Alex Developer" in response.data

    # Logout
    logout_response = client.post("/auth/logout", follow_redirects=True)
    assert logout_response.status_code == 200
    assert b"You have been signed out." in logout_response.data


def test_invalid_login_credentials(client, test_user):
    """Test that invalid password or unregistered email returns 401."""
    # Wrong password
    response_wrong_pw = client.post(
        "/auth/login",
        data={
            "email": test_user.email,
            "password": "WrongPassword999!",
        },
    )
    assert response_wrong_pw.status_code == 401
    assert b"Invalid email or password." in response_wrong_pw.data

    # Unregistered email
    response_unknown = client.post(
        "/auth/login",
        data={
            "email": "nonexistent@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert response_unknown.status_code == 401
    assert b"Invalid email or password." in response_unknown.data


def test_open_redirect_prevention(client, test_user):
    """Test that unsafe external next redirects are blocked."""
    response = client.post(
        "/auth/login?next=https://malicious-external-site.com",
        data={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/")


def test_protected_route_redirect(client):
    """Test unauthenticated access to protected dashboard redirects to login."""
    response = client.get("/dashboard/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
