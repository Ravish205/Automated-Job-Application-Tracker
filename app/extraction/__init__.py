from flask import Blueprint

extraction_bp = Blueprint("extraction", __name__, url_prefix="/extraction")

from app.extraction import routes  # noqa: E402, F401

