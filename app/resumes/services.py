import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.activity import Activity, ActivityEventType
from app.models.resume import Resume

ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream",  # Fallback often reported by some browsers for docx
}


def is_allowed_file(filename: str) -> bool:
    """Validate file extension against allowed whitelist."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_resume_file(file: FileStorage, user_id: int) -> tuple[Resume | None, str | None]:
    """
    Validate, sanitize, and save an uploaded resume to private storage.
    Returns (Resume, None) on success or (None, error_message) on failure.
    """
    if not file or not file.filename:
        return None, "No file selected for upload."

    original_filename = secure_filename(file.filename)
    if not original_filename:
        return None, "Invalid filename."

    if not is_allowed_file(original_filename):
        return None, "Only PDF (.pdf) and Word documents (.docx) are supported."

    # Validate file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    max_size_bytes = current_app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return None, f"File exceeds maximum allowed size of {max_mb:.0f} MB."

    if file_size == 0:
        return None, "The uploaded file is empty."

    # Verify content type
    content_type = file.content_type or "application/octet-stream"
    extension = original_filename.rsplit(".", 1)[1].lower()

    # Generate unique UUID-based filename on disk to prevent collisions and directory traversal
    stored_filename = f"{uuid.uuid4().hex}_{user_id}.{extension}"
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / stored_filename
    file.save(str(file_path))

    # Persist database record
    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        file_size=file_size,
    )
    db.session.add(resume)
    db.session.flush()

    # Log activity
    activity = Activity(
        user_id=user_id,
        event_type=ActivityEventType.RESUME_UPLOADED,
        description=f"Uploaded resume '{original_filename}'",
    )
    db.session.add(activity)
    db.session.commit()

    return resume, None


def delete_resume_file(resume: Resume) -> bool:
    """Delete the physical resume file from disk and its database record."""
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    file_path = upload_folder / resume.stored_filename

    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            current_app.logger.error(f"Error removing file {file_path}: {e}")

    db.session.delete(resume)
    db.session.commit()
    return True
