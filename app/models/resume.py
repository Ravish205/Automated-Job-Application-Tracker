from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    pass


class Resume(db.Model):
    """Uploaded resume file metadata."""

    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user = db.relationship("User", back_populates="resumes")
    applications = db.relationship("Application", back_populates="resume")

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file='{self.original_filename}'>"
