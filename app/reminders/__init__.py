from flask import Blueprint

reminders_bp = Blueprint("reminders", __name__, url_prefix="/reminders")

from app.reminders import routes  # noqa: E402, F401

