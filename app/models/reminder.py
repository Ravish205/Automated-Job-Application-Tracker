from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    pass


class ReminderStatus:
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    DISMISSED = "Dismissed"

    CHOICES = [PENDING, COMPLETED, CANCELLED, DISMISSED]


class Reminder(db.Model):
    """Deadline and interview reminder."""

    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    reminder_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    status = db.Column(
        db.String(50),
        nullable=False,
        default=ReminderStatus.PENDING,
    )
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    user = db.relationship("User", back_populates="reminders")
    application = db.relationship("Application", back_populates="reminders")
    interview = db.relationship("Interview", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} at={self.reminder_at} status='{self.status}'>"
