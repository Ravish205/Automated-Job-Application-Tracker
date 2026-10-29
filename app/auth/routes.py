from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models.activity import Activity, ActivityEventType
from app.models.user import User


def is_safe_url(target: str, host_url: str) -> bool:
    """Ensure a redirection target is internal and safe against open redirect attacks."""
    if not target:
        return False
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user account registration."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        normalized_email = form.email.data.strip().lower()

        # Check for existing email
        existing_user = db.session.execute(
            db.select(User).filter_by(email=normalized_email)
        ).scalar_one_or_none()

        if existing_user:
            form.email.errors.append("An account with this email address already exists.")
            flash("An account with this email address already exists.", "error")
            return render_template("auth/register.html", form=form), 400

        # Create new user
        new_user = User(
            full_name=form.full_name.data.strip(),
            email=normalized_email,
            timezone="UTC",
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.flush()  # Flush to get the new_user.id for activity logging

        # Record initial registration activity
        activity = Activity(
            user_id=new_user.id,
            event_type=ActivityEventType.APPLICATION_CREATED,
            description="Account registered",
        )
        db.session.add(activity)
        db.session.commit()

        login_user(new_user)
        flash("Account created successfully! Welcome to your Job Tracker.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user authentication and session establishment."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        normalized_email = form.email.data.strip().lower()
        user = db.session.execute(
            db.select(User).filter_by(email=normalized_email)
        ).scalar_one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", form=form), 401

        login_user(user, remember=form.remember_me.data)
        flash("Signed in successfully.", "success")

        next_page = request.args.get("next")
        if not next_page or not is_safe_url(next_page, request.host_url):
            next_page = url_for("dashboard.index")

        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Terminate user session securely."""
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("landing"))
