from datetime import UTC, datetime

from flask import render_template
from flask_login import current_user, login_required

from app.dashboard import dashboard_bp
from app.extensions import db
from app.models.activity import Activity
from app.models.application import Application, ApplicationStatus, Interview


@dashboard_bp.route("/")
@login_required
def index():
    """Calculate and display real dashboard metrics and recent records."""
    now_utc = datetime.now(UTC)

    # 1. Metric: Total Applications
    total_applications = (
        db.session.execute(
            db.select(db.func.count(Application.id)).filter_by(user_id=current_user.id)
        ).scalar()
        or 0
    )

    # 2. Metric: Active Applications (Applied, Assessment, Interview)
    active_applications = (
        db.session.execute(
            db.select(db.func.count(Application.id)).filter(
                Application.user_id == current_user.id,
                Application.status.in_(
                    [
                        ApplicationStatus.APPLIED,
                        ApplicationStatus.ASSESSMENT,
                        ApplicationStatus.INTERVIEW,
                    ]
                ),
            )
        ).scalar()
        or 0
    )

    # 3. Metric: Interviews (Scheduled)
    interviews_count = (
        db.session.execute(
            db.select(db.func.count(Interview.id))
            .join(Application)
            .filter(Application.user_id == current_user.id)
        ).scalar()
        or 0
    )

    # 4. Metric: Offers
    offers_count = (
        db.session.execute(
            db.select(db.func.count(Application.id)).filter(
                Application.user_id == current_user.id,
                Application.status == ApplicationStatus.OFFER,
            )
        ).scalar()
        or 0
    )

    # 5. Upcoming Deadlines
    upcoming_deadlines_query = (
        db.select(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.deadline.isnot(None),
            Application.status.notin_(
                [ApplicationStatus.OFFER, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]
            ),
        )
        .order_by(Application.deadline.asc())
        .limit(5)
    )
    upcoming_deadlines = db.session.execute(upcoming_deadlines_query).scalars().all()

    # 6. Recent Applications (up to 5)
    recent_applications = (
        db.session.execute(
            db.select(Application)
            .filter_by(user_id=current_user.id)
            .order_by(Application.created_at.desc())
            .limit(5)
        )
        .scalars()
        .all()
    )

    # 7. Recent Activities (up to 6)
    recent_activities = (
        db.session.execute(
            db.select(Activity)
            .filter_by(user_id=current_user.id)
            .order_by(Activity.created_at.desc())
            .limit(6)
        )
        .scalars()
        .all()
    )

    return render_template(
        "dashboard/index.html",
        total_applications=total_applications,
        active_applications=active_applications,
        interviews_count=interviews_count,
        offers_count=offers_count,
        upcoming_deadlines=upcoming_deadlines,
        recent_applications=recent_applications,
        recent_activities=recent_activities,
        now_utc=now_utc,
    )
