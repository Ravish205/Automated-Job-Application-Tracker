import os

from app import create_app
from app.extensions import db
from app.models import Activity, Application, Interview, Reminder, Resume, User

app = create_app(os.getenv("FLASK_CONFIG", "default"))


@app.shell_context_processor
def make_shell_context():
    """Configure interactive Flask shell context with models and db."""
    return {
        "db": db,
        "User": User,
        "Application": Application,
        "Interview": Interview,
        "Resume": Resume,
        "Reminder": Reminder,
        "Activity": Activity,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
