from datetime import UTC, datetime

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.applications import applications_bp
from app.applications.forms import ApplicationForm
from app.applications.services import (
    get_filtered_applications,
    log_application_activity,
    populate_resume_choices,
)
from app.extensions import db
from app.models.activity import ActivityEventType
from app.models.application import Application, ApplicationStatus, WorkArrangement


@applications_bp.route("/", methods=["GET"])
@login_required
def index():
    """List applications with search, status filtering, sorting, and pagination."""
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    arrangement_filter = request.args.get("arrangement", "").strip()
    sort_by = request.args.get("sort", "created_desc").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = get_filtered_applications(
        user_id=current_user.id,
        search_query=search_query,
        status_filter=status_filter,
        arrangement_filter=arrangement_filter,
        sort_by=sort_by,
    )

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return render_template(
        "applications/index.html",
        applications=pagination.items,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
        arrangement_filter=arrangement_filter,
        sort_by=sort_by,
        statuses=ApplicationStatus.CHOICES,
        arrangements=WorkArrangement.CHOICES,
    )


@applications_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    """Create a new job application."""
    form = ApplicationForm()
    populate_resume_choices(form, current_user.id)

    if form.validate_on_submit():
        resume_id_val = form.resume_id.data if form.resume_id.data != 0 else None

        # Convert deadline to timezone-aware UTC datetime if provided
        deadline_dt = None
        if form.deadline.data:
            deadline_dt = datetime.combine(
                form.deadline.data,
                datetime.min.time(),
                tzinfo=UTC,
            )

        application = Application(
            user_id=current_user.id,
            company_name=form.company_name.data.strip(),
            job_title=form.job_title.data.strip(),
            job_url=form.job_url.data.strip() if form.job_url.data else None,
            location=form.location.data.strip() if form.location.data else None,
            employment_type=form.employment_type.data or None,
            work_arrangement=form.work_arrangement.data or None,
            salary=form.salary.data.strip() if form.salary.data else None,
            status=form.status.data,
            applied_at=form.applied_at.data,
            deadline=deadline_dt,
            resume_id=resume_id_val,
            notes=form.notes.data.strip() if form.notes.data else None,
        )

        db.session.add(application)
        db.session.commit()

        log_application_activity(
            user_id=current_user.id,
            application_id=application.id,
            event_type=ActivityEventType.APPLICATION_CREATED,
            description=f"Created application for {application.company_name} - {application.job_title}",
        )

        flash(f"Application for '{application.company_name}' created successfully.", "success")
        return redirect(url_for("applications.detail", app_id=application.id))

    return render_template("applications/create.html", form=form)


@applications_bp.route("/<int:app_id>", methods=["GET"])
@login_required
def detail(app_id: int):
    """View application details, interviews, resume, and audit history."""
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)

    if application.user_id != current_user.id:
        abort(403)

    return render_template(
        "applications/detail.html",
        application=application,
        statuses=ApplicationStatus.CHOICES,
    )


@applications_bp.route("/<int:app_id>/edit", methods=["GET", "POST"])
@login_required
def edit(app_id: int):
    """Edit an existing job application."""
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)

    if application.user_id != current_user.id:
        abort(403)

    form = ApplicationForm(obj=application)
    populate_resume_choices(form, current_user.id)

    if request.method == "GET":
        if application.resume_id:
            form.resume_id.data = application.resume_id
        if application.deadline:
            form.deadline.data = application.deadline.date()

    if form.validate_on_submit():
        prev_status = application.status
        resume_id_val = form.resume_id.data if form.resume_id.data != 0 else None

        deadline_dt = None
        if form.deadline.data:
            deadline_dt = datetime.combine(
                form.deadline.data,
                datetime.min.time(),
                tzinfo=UTC,
            )

        application.company_name = form.company_name.data.strip()
        application.job_title = form.job_title.data.strip()
        application.job_url = form.job_url.data.strip() if form.job_url.data else None
        application.location = form.location.data.strip() if form.location.data else None
        application.employment_type = form.employment_type.data or None
        application.work_arrangement = form.work_arrangement.data or None
        application.salary = form.salary.data.strip() if form.salary.data else None
        application.status = form.status.data
        application.applied_at = form.applied_at.data
        application.deadline = deadline_dt
        application.resume_id = resume_id_val
        application.notes = form.notes.data.strip() if form.notes.data else None

        db.session.commit()

        if prev_status != application.status:
            log_application_activity(
                user_id=current_user.id,
                application_id=application.id,
                event_type=ActivityEventType.STATUS_CHANGED,
                description=f"Status changed from {prev_status} to {application.status}",
            )
        else:
            log_application_activity(
                user_id=current_user.id,
                application_id=application.id,
                event_type=ActivityEventType.APPLICATION_UPDATED,
                description="Updated application details",
            )

        flash("Application updated successfully.", "success")
        return redirect(url_for("applications.detail", app_id=application.id))

    return render_template("applications/edit.html", form=form, application=application)


@applications_bp.route("/<int:app_id>/status", methods=["POST"])
@login_required
def update_status(app_id: int):
    """Quickly update application status."""
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)

    if application.user_id != current_user.id:
        abort(403)

    new_status = request.form.get("status")
    if new_status in ApplicationStatus.CHOICES and new_status != application.status:
        prev_status = application.status
        application.status = new_status
        db.session.commit()

        log_application_activity(
            user_id=current_user.id,
            application_id=application.id,
            event_type=ActivityEventType.STATUS_CHANGED,
            description=f"Status changed from {prev_status} to {new_status}",
        )
        flash(f"Status updated to '{new_status}'.", "success")

    return redirect(request.referrer or url_for("applications.detail", app_id=application.id))


@applications_bp.route("/<int:app_id>/delete", methods=["POST"])
@login_required
def delete(app_id: int):
    """Delete an application."""
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)

    if application.user_id != current_user.id:
        abort(403)

    company = application.company_name
    db.session.delete(application)
    db.session.commit()

    flash(f"Application for '{company}' has been deleted.", "info")
    return redirect(url_for("applications.index"))
