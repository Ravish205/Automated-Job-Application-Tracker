from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    pass


class ApplicationStatus:
    SAVED = "Saved"
    APPLIED = "Applied"
    ASSESSMENT = "Assessment"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

    CHOICES = [SAVED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN]


class EmploymentType:
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"

    CHOICES = [FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP, FREELANCE]


class WorkArrangement:
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"

    CHOICES = [REMOTE, HYBRID, ON_SITE]


class Application(db.Model):
    """Job application record."""

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name = db.Column(db.String(150), nullable=False, index=True)
    job_title = db.Column(db.String(150), nullable=False, index=True)
    job_url = db.Column(db.String(1024), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)
    work_arrangement = db.Column(db.String(50), nullable=True)
    salary = db.Column(db.String(100), nullable=True)
    status = db.Column(
        db.String(50),
        nullable=False,
        default=ApplicationStatus.APPLIED,
        index=True,
    )
    applied_at = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)
    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user = db.relationship("User", back_populates="applications")
    resume = db.relationship("Resume", back_populates="applications")
    interviews = db.relationship(
        "Interview",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="Interview.scheduled_at.asc()",
        lazy="selectin",
    )
    reminders = db.relationship(
        "Reminder",
        back_populates="application",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    activities = db.relationship(
        "Activity",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="Activity.created_at.desc()",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Application id={self.id} company='{self.company_name}' title='{self.job_title}'>"


class InterviewType:
    PHONE_SCREENING = "Phone screening"
    TECHNICAL = "Technical interview"
    HR = "HR interview"
    HIRING_MANAGER = "Hiring manager interview"
    FINAL = "Final interview"
    OTHER = "Other"

    CHOICES = [PHONE_SCREENING, TECHNICAL, HR, HIRING_MANAGER, FINAL, OTHER]


class InterviewStatus:
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

    CHOICES = [SCHEDULED, COMPLETED, CANCELLED]


class Interview(db.Model):
    """Interview stage associated with an application."""

    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interview_type = db.Column(db.String(50), nullable=False)
    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    timezone = db.Column(db.String(50), nullable=False, default="UTC")
    meeting_location = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50),
        nullable=False,
        default=InterviewStatus.SCHEDULED,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    application = db.relationship("Application", back_populates="interviews")
    reminders = db.relationship(
        "Reminder",
        back_populates="interview",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Interview id={self.id} app_id={self.application_id} type='{self.interview_type}'>"
