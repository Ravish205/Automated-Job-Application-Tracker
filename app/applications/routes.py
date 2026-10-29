from flask import render_template
from flask_login import login_required

from app.applications import applications_bp


@applications_bp.route("/")
@login_required
def index():
    return render_template("applications/index.html")
