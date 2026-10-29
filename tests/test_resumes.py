import io

from app.extensions import db
from app.models.resume import Resume
from app.models.user import User


def login_user(client, user, password="SecurePassword123!"):
    """Helper to authenticate test client."""
    return client.post(
        "/auth/login",
        data={"email": user.email, "password": password},
        follow_redirects=True,
    )


def test_upload_resume_pdf(client, test_user, db_session):
    """Test successfully uploading a PDF resume document."""
    login_user(client, test_user)

    data = {
        "resume_file": (io.BytesIO(b"%PDF-1.4 sample pdf content"), "software_engineer_cv.pdf"),
    }
    response = client.post(
        "/resumes/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"software_engineer_cv.pdf" in response.data

    resume = db_session.execute(
        db.select(Resume).filter_by(
            user_id=test_user.id, original_filename="software_engineer_cv.pdf"
        )
    ).scalar_one_or_none()
    assert resume is not None
    assert resume.file_size > 0
    assert resume.stored_filename.endswith(".pdf")


def test_upload_resume_docx(client, test_user, db_session):
    """Test successfully uploading a DOCX resume document."""
    login_user(client, test_user)

    data = {
        "resume_file": (io.BytesIO(b"PK\x03\x04 fake docx binary data"), "developer_resume.docx"),
    }
    response = client.post(
        "/resumes/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"developer_resume.docx" in response.data


def test_reject_unsupported_file_extension(client, test_user):
    """Test that executable or unsupported file types are rejected."""
    login_user(client, test_user)

    data = {
        "resume_file": (io.BytesIO(b"echo 'malicious script'"), "payload.sh"),
    }
    response = client.post(
        "/resumes/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Only PDF (.pdf) and Word documents (.docx) are permitted." in response.data
        or b"error" in response.data
    )


def test_download_resume(client, test_user, db_session):
    """Test downloading an owned resume document."""
    login_user(client, test_user)

    # First upload
    data = {
        "resume_file": (io.BytesIO(b"%PDF-1.4 test download file"), "my_cv.pdf"),
    }
    client.post("/resumes/upload", data=data, content_type="multipart/form-data")

    resume = db_session.execute(
        db.select(Resume).filter_by(user_id=test_user.id, original_filename="my_cv.pdf")
    ).scalar_one()

    # Download
    download_res = client.get(f"/resumes/{resume.id}/download")
    assert download_res.status_code == 200
    assert download_res.data == b"%PDF-1.4 test download file"
    assert "attachment" in download_res.headers.get("Content-Disposition", "")
    assert "my_cv.pdf" in download_res.headers.get("Content-Disposition", "")


def test_cross_user_resume_isolation(client, test_user, db_session):
    """Test that users cannot access or delete other users' resumes."""
    other_user = User(full_name="Second User", email="second@example.com")
    other_user.set_password("SecurePassword123!")
    db_session.add(other_user)
    db_session.flush()

    login_user(client, other_user)
    data = {
        "resume_file": (io.BytesIO(b"%PDF-1.4 confidential resume"), "private_resume.pdf"),
    }
    client.post("/resumes/upload", data=data, content_type="multipart/form-data")

    other_resume = db_session.execute(
        db.select(Resume).filter_by(user_id=other_user.id)
    ).scalar_one()

    # Logout and switch to test_user
    client.post("/auth/logout")
    login_user(client, test_user)

    # Attempt to download other's resume
    down_res = client.get(f"/resumes/{other_resume.id}/download")
    assert down_res.status_code == 403

    # Attempt to delete other's resume
    del_res = client.post(f"/resumes/{other_resume.id}/delete")
    assert del_res.status_code == 403


def test_delete_resume(client, test_user, db_session):
    """Test deleting an uploaded resume."""
    login_user(client, test_user)

    data = {
        "resume_file": (io.BytesIO(b"%PDF-1.4 file to delete"), "to_delete.pdf"),
    }
    client.post("/resumes/upload", data=data, content_type="multipart/form-data")

    resume = db_session.execute(
        db.select(Resume).filter_by(user_id=test_user.id, original_filename="to_delete.pdf")
    ).scalar_one()

    del_res = client.post(f"/resumes/{resume.id}/delete", follow_redirects=True)
    assert del_res.status_code == 200
    assert b"has been deleted" in del_res.data

    check = db_session.get(Resume, resume.id)
    assert check is None
