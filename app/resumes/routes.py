from pathlib import Path

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models.resume import Resume
from app.resumes import resumes_bp
from app.resumes.forms import ResumeUploadForm
from app.resumes.services import delete_resume_file, save_resume_file


@resumes_bp.route("/", methods=["GET"])
@login_required
def index():
    """List all resumes uploaded by the authenticated user."""
    resumes = (
        db.session.execute(
            db.select(Resume).filter_by(user_id=current_user.id).order_by(Resume.created_at.desc())
        )
        .scalars()
        .all()
    )

    upload_form = ResumeUploadForm()
    return render_template("resumes/index.html", resumes=resumes, upload_form=upload_form)


@resumes_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """Handle resume file upload."""
    form = ResumeUploadForm()
    if form.validate_on_submit():
        file = form.resume_file.data
        resume, error = save_resume_file(file, current_user.id)
        if error:
            flash(error, "error")
        else:
            flash(f"Resume '{resume.original_filename}' uploaded successfully.", "success")
    else:
        for _field, errors in form.errors.items():
            for err in errors:
                flash(err, "error")

    return redirect(url_for("resumes.index"))


@resumes_bp.route("/<int:resume_id>/download", methods=["GET"])
@login_required
def download(resume_id: int):
    """Download a resume file if owned by authenticated user."""
    resume = db.session.get(Resume, resume_id)
    if resume is None:
        abort(404)

    if resume.user_id != current_user.id:
        abort(403)

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    file_path = upload_folder / resume.stored_filename
    if not file_path.exists():
        flash("Resume file is no longer available on disk.", "error")
        return redirect(url_for("resumes.index"))

    return send_from_directory(
        directory=upload_folder,
        path=resume.stored_filename,
        as_attachment=True,
        download_name=resume.original_filename,
    )


@resumes_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id: int):
    """Delete a resume if owned by authenticated user."""
    resume = db.session.get(Resume, resume_id)
    if resume is None:
        abort(404)

    if resume.user_id != current_user.id:
        abort(403)

    filename = resume.original_filename
    delete_resume_file(resume)
    flash(f"Resume '{filename}' has been deleted.", "info")
    return redirect(url_for("resumes.index"))
