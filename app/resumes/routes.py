from flask import render_template
from flask_login import login_required

from app.resumes import resumes_bp


@resumes_bp.route("/")
@login_required
def index():
    return render_template("resumes/index.html")
