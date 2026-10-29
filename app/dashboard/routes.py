from flask import render_template
from flask_login import current_user, login_required

from app.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.html", user=current_user)
