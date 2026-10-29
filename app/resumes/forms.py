from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField


class ResumeUploadForm(FlaskForm):
    """Form to securely upload a resume document."""

    resume_file = FileField(
        "Select Resume File",
        validators=[
            FileRequired(message="Please select a file to upload."),
            FileAllowed(
                ["pdf", "docx"], message="Only PDF (.pdf) and Word documents (.docx) are permitted."
            ),
        ],
    )
    submit = SubmitField("Upload resume")
