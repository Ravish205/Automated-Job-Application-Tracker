from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    pass


class ActivityEventType:
    APPLICATION_CREATED = "application_created"
    APPLICATION_UPDATED = "application_updated"
    APPLICATION_DELETED = "application_deleted"
    STATUS_CHANGED = "status_changed"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    RESUME_ATTACHED = "resume_attached"
    RESUME_UPLOADED = "resume_uploaded"
    REMINDER_CREATED = "reminder_created"


class Activity(db.Model):
    """User and application activity audit trail."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    # Relationships
    user = db.relationship("User", back_populates="activities")
    application = db.relationship("Application", back_populates="activities")

    def __repr__(self) -> str:
        return f"<Activity id={self.id} event='{self.event_type}'>"
