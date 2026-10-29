from app.extensions import db
from app.models.application import Application, ApplicationStatus
from app.models.user import User


def login_user(client, user, password="SecurePassword123!"):
    """Helper to authenticate test client."""
    return client.post(
        "/auth/login",
        data={"email": user.email, "password": password},
        follow_redirects=True,
    )


def test_create_application(client, test_user, db_session):
    """Test creating a new job application."""
    login_user(client, test_user)

    response = client.post(
        "/applications/new",
        data={
            "company_name": "Stripe",
            "job_title": "Backend Infrastructure Engineer",
            "job_url": "https://stripe.com/jobs/123",
            "location": "Remote - US",
            "employment_type": "Full-time",
            "work_arrangement": "Remote",
            "salary": "$175,000",
            "status": "Applied",
            "applied_at": "2026-10-15",
            "notes": "Referred by engineering manager.",
            "resume_id": 0,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Application for &#39;Stripe&#39; created successfully" in response.data
        or b"Stripe" in response.data
    )

    app_record = db_session.execute(
        db.select(Application).filter_by(user_id=test_user.id, company_name="Stripe")
    ).scalar_one_or_none()
    assert app_record is not None
    assert app_record.job_title == "Backend Infrastructure Engineer"
    assert app_record.status == ApplicationStatus.APPLIED
    assert app_record.work_arrangement == "Remote"


def test_application_validation_error(client, test_user):
    """Test validation errors when required fields are missing."""
    login_user(client, test_user)

    # Missing company name
    response = client.post(
        "/applications/new",
        data={
            "company_name": "",
            "job_title": "Software Engineer",
            "status": "Applied",
        },
    )
    assert response.status_code == 200
    assert b"Company name is required." in response.data


def test_edit_application(client, test_user, db_session):
    """Test editing an existing application."""
    login_user(client, test_user)

    app = Application(
        user_id=test_user.id,
        company_name="Datadog",
        job_title="Software Engineer",
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(app)
    db_session.commit()

    response = client.post(
        f"/applications/{app.id}/edit",
        data={
            "company_name": "Datadog Inc",
            "job_title": "Senior Software Engineer",
            "status": "Interview",
            "notes": "Passed technical phone screen.",
            "resume_id": 0,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Application updated successfully." in response.data

    db_session.refresh(app)
    assert app.company_name == "Datadog Inc"
    assert app.job_title == "Senior Software Engineer"
    assert app.status == ApplicationStatus.INTERVIEW


def test_quick_status_update(client, test_user, db_session):
    """Test updating application status via dedicated endpoint."""
    login_user(client, test_user)

    app = Application(
        user_id=test_user.id,
        company_name="Figma",
        job_title="Frontend Developer",
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(app)
    db_session.commit()

    response = client.post(
        f"/applications/{app.id}/status",
        data={"status": ApplicationStatus.OFFER},
        follow_redirects=True,
    )
    assert response.status_code == 200
    db_session.refresh(app)
    assert app.status == ApplicationStatus.OFFER


def test_delete_application(client, test_user, db_session):
    """Test deleting an application."""
    login_user(client, test_user)

    app = Application(
        user_id=test_user.id,
        company_name="Netflix",
        job_title="Streaming Engineer",
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(app)
    db_session.commit()

    response = client.post(
        f"/applications/{app.id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Application for &#39;Netflix&#39; has been deleted." in response.data
        or b"Netflix" in response.data
    )

    app_check = db_session.get(Application, app.id)
    assert app_check is None


def test_cross_user_application_isolation(client, test_user, db_session):
    """Verify that a user cannot access or modify another user's application."""
    # Create second user and application
    other_user = User(full_name="Other Candidate", email="other@example.com")
    other_user.set_password("SecurePassword123!")
    db_session.add(other_user)
    db_session.flush()

    other_app = Application(
        user_id=other_user.id,
        company_name="Private Corp",
        job_title="Internal Auditor",
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(other_app)
    db_session.commit()

    # Login as first user
    login_user(client, test_user)

    # Attempt to view
    view_res = client.get(f"/applications/{other_app.id}")
    assert view_res.status_code == 403

    # Attempt to edit
    edit_res = client.post(
        f"/applications/{other_app.id}/edit",
        data={
            "company_name": "Hacked Corp",
            "job_title": "Hacker",
            "status": "Offer",
            "resume_id": 0,
        },
    )
    assert edit_res.status_code == 403

    # Attempt to delete
    del_res = client.post(f"/applications/{other_app.id}/delete")
    assert del_res.status_code == 403

    # Verify other_app is unchanged
    db_session.refresh(other_app)
    assert other_app.company_name == "Private Corp"


def test_applications_search_and_filter(client, test_user, db_session):
    """Test filtering applications by status and search keyword."""
    login_user(client, test_user)

    app1 = Application(
        user_id=test_user.id,
        company_name="Google",
        job_title="Cloud Engineer",
        status=ApplicationStatus.APPLIED,
    )
    app2 = Application(
        user_id=test_user.id,
        company_name="Microsoft",
        job_title="Systems Engineer",
        status=ApplicationStatus.INTERVIEW,
    )
    db_session.add_all([app1, app2])
    db_session.commit()

    # Filter by search term
    search_res = client.get("/applications/?q=Google")
    assert search_res.status_code == 200
    assert b"Google" in search_res.data
    assert b"Microsoft" not in search_res.data

    # Filter by status
    status_res = client.get("/applications/?status=Interview")
    assert status_res.status_code == 200
    assert b"Microsoft" in status_res.data
    assert b"Google" not in status_res.data
