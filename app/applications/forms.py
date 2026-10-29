from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import URL, DataRequired, Length, Optional

from app.models.application import (
    ApplicationStatus,
    EmploymentType,
    WorkArrangement,
)


class ApplicationForm(FlaskForm):
    """Job application creation and edit form."""

    company_name = StringField(
        "Company Name",
        validators=[
            DataRequired(message="Company name is required."),
            Length(max=150, message="Company name must be under 150 characters."),
        ],
    )
    job_title = StringField(
        "Job Title",
        validators=[
            DataRequired(message="Job title is required."),
            Length(max=150, message="Job title must be under 150 characters."),
        ],
    )
    job_url = StringField(
        "Job Posting URL",
        validators=[
            Optional(),
            URL(message="Please provide a valid web URL."),
            Length(max=1024, message="URL is too long."),
        ],
    )
    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=150, message="Location must be under 150 characters."),
        ],
    )
    employment_type = SelectField(
        "Employment Type",
        choices=[("", "Select employment type")] + [(c, c) for c in EmploymentType.CHOICES],
        validators=[Optional()],
    )
    work_arrangement = SelectField(
        "Work Arrangement",
        choices=[("", "Select arrangement")] + [(c, c) for c in WorkArrangement.CHOICES],
        validators=[Optional()],
    )
    salary = StringField(
        "Salary / Compensation",
        validators=[
            Optional(),
            Length(max=100, message="Salary description must be under 100 characters."),
        ],
    )
    status = SelectField(
        "Application Status",
        choices=[(c, c) for c in ApplicationStatus.CHOICES],
        default=ApplicationStatus.APPLIED,
        validators=[DataRequired(message="Status is required.")],
    )
    applied_at = DateField(
        "Application Date",
        validators=[Optional()],
    )
    deadline = DateField(
        "Deadline",
        validators=[Optional()],
    )
    resume_id = SelectField(
        "Resume Used",
        coerce=int,
        choices=[(0, "No resume associated")],
        validators=[Optional()],
    )
    notes = TextAreaField(
        "Notes & Observations",
        validators=[Optional()],
    )
    submit = SubmitField("Save application")
