from sqlalchemy import or_

from app.extensions import db
from app.models.activity import Activity
from app.models.application import Application, ApplicationStatus
from app.models.resume import Resume


def populate_resume_choices(form, user_id: int) -> None:
    """Populate resume select options with resumes belonging to the user."""
    resumes = (
        db.session.execute(
            db.select(Resume).filter_by(user_id=user_id).order_by(Resume.created_at.desc())
        )
        .scalars()
        .all()
    )

    choices = [(0, "No resume associated")]
    for r in resumes:
        choices.append((r.id, r.original_filename))
    form.resume_id.choices = choices


def get_filtered_applications(
    user_id: int,
    search_query: str | None = None,
    status_filter: str | None = None,
    arrangement_filter: str | None = None,
    sort_by: str | None = None,
):
    """Build a filtered and sorted query for user applications."""
    query = db.select(Application).filter_by(user_id=user_id)

    if search_query:
        term = f"%{search_query.strip()}%"
        query = query.filter(
            or_(
                Application.company_name.ilike(term),
                Application.job_title.ilike(term),
                Application.location.ilike(term),
            )
        )

    if status_filter and status_filter in ApplicationStatus.CHOICES:
        query = query.filter(Application.status == status_filter)

    if arrangement_filter:
        query = query.filter(Application.work_arrangement == arrangement_filter)

    # Sorting
    if sort_by == "created_asc":
        query = query.order_by(Application.created_at.asc())
    elif sort_by == "company_asc":
        query = query.order_by(Application.company_name.asc())
    elif sort_by == "deadline_asc":
        query = query.order_by(Application.deadline.asc().nullslast())
    elif sort_by == "applied_desc":
        query = query.order_by(Application.applied_at.desc().nullslast())
    else:  # default created_desc
        query = query.order_by(Application.created_at.desc())

    return query


def log_application_activity(user_id: int, application_id: int, event_type: str, description: str):
    """Record an audit trail activity for the user and application."""
    activity = Activity(
        user_id=user_id,
        application_id=application_id,
        event_type=event_type,
        description=description,
    )
    db.session.add(activity)
    db.session.commit()
