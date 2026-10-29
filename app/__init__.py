import logging
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from app.config import config_by_name
from app.extensions import csrf, db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for the Automated Job Application Tracker."""

    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "default")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(app)

    # Ensure uploads directory exists
    upload_dir = Path(app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Setup User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # Register blueprints
    register_blueprints(app)

    # Register root / landing route
    @app.route("/")
    def landing():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("landing.html")

    # Register custom error handlers
    register_error_handlers(app)

    # Global context processor
    @app.context_processor
    def inject_global_vars():
        return {
            "app_name": "Automated Job Application Tracker",
        }

    return app


def register_blueprints(app: Flask) -> None:
    """Register all modular application blueprints."""
    from app.analytics import analytics_bp
    from app.api import api_bp
    from app.applications import applications_bp
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.extraction import extraction_bp
    from app.reminders import reminders_bp
    from app.resumes import resumes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(extraction_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)


def register_error_handlers(app: Flask) -> None:
    """Register handlers for standard HTTP errors with HTML and JSON support."""

    def is_api_request() -> bool:
        return (
            request.path.startswith("/api/") or request.headers.get("Accept") == "application/json"
        )

    @app.errorhandler(400)
    def bad_request(error):
        if is_api_request():
            return jsonify({"error": "Bad Request", "message": str(error)}), 400
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        if is_api_request():
            return jsonify({"error": "Forbidden", "message": "Access denied"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        if is_api_request():
            return jsonify({"error": "Not Found", "message": "Resource not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def payload_too_large(error):
        if is_api_request():
            return jsonify(
                {"error": "Payload Too Large", "message": "File exceeds size limit"}
            ), 413
        return render_template("errors/413.html"), 413

    @app.errorhandler(429)
    def too_many_requests(error):
        if is_api_request():
            return jsonify({"error": "Too Many Requests", "message": "Rate limit exceeded"}), 429
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        if is_api_request():
            return jsonify(
                {"error": "Internal Server Error", "message": "An unexpected error occurred"}
            ), 500
        return render_template("errors/500.html"), 500


def configure_logging(app: Flask) -> None:
    """Configure secure and structured application logging."""
    if not app.debug and not app.testing:
        log_level = logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        )
