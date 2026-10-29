from flask import render_template
from flask_login import login_required

from app.reminders import reminders_bp


@reminders_bp.route("/")
@login_required
def index():
    return render_template("reminders/index.html")
