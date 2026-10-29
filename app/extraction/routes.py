from flask import jsonify
from flask_login import login_required

from app.extraction import extraction_bp


@extraction_bp.route("/ping")
@login_required
def ping():
    return jsonify({"status": "ok", "service": "extraction"})
