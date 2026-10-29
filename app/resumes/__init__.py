from flask import Blueprint

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")

from app.resumes import routes  # noqa: E402, F401
