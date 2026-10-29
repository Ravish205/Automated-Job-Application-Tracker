from datetime import UTC, datetime, timedelta

from app.models.application import Application, ApplicationStatus


def login_user(client, user, password="SecurePassword123!"):
    """Helper to authenticate test client."""
    return client.post(
        "/auth/login",
        data={"email": user.email, "password": password},
        follow_redirects=True,
    )


def test_dashboard_empty_state(client, test_user):
    """Test dashboard shows required empty state when no applications exist."""
    login_user(client, test_user)

    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"No applications yet" in response.data
    assert b"Start tracking your job search by adding your first application." in response.data
    assert b"Add application" in response.data


def test_dashboard_metrics_calculation(client, test_user, db_session):
    """Test dashboard metrics reflect actual database records."""
    login_user(client, test_user)

    now = datetime.now(UTC)
    app1 = Application(
        user_id=test_user.id,
        company_name="Amazon",
        job_title="DevOps Engineer",
        status=ApplicationStatus.APPLIED,
        deadline=now + timedelta(days=5),
    )
    app2 = Application(
        user_id=test_user.id,
        company_name="Apple",
        job_title="iOS Developer",
        status=ApplicationStatus.OFFER,
    )
    db_session.add_all([app1, app2])
    db_session.commit()

    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"Total Applications" in response.data
    assert b"Amazon" in response.data
    assert b"Apple" in response.data
    assert b"5 days left" in response.data
