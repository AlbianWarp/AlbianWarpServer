from warpserver.util import web_admin_required, web_token_required
from flask import Blueprint, render_template, session, request

from warpserver.model.base import db

from warpserver.model import User

admin_page_blueprint = Blueprint("admin", __name__, template_folder="templates")


@admin_page_blueprint.route("/admin", methods=["GET"])
@web_token_required
@web_admin_required
def admin_overview():
    return render_template("admin_dashboard.html", session=session)


@admin_page_blueprint.route("/admin/user", methods=["GET"])
@web_token_required
@web_admin_required
def admin_user_overview():
    users = db.session.query(User).all()
    users_dict = []
    for user in users:
        users_dict.append(
            {
                "id": user.id,
                "name": user.username,
                "email": user.email,
                "power": user.power,
            }
        )
    return render_template("admin_user_overview.html", users=users, session=session)


@admin_page_blueprint.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
@web_token_required
@web_admin_required
def admin_user(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return render_template("error.html", message="User not found!"), 404
    message = None
    if request.method == "POST":
        if "password" in request.form and request.form["password"] != "":
            user.password_hash = user.hash_password(request.form["password"])
        if "username" in request.form and request.form["username"] != "":
            user.username = request.form["username"]
        if (
            "email" in request.form
            and request.form["email"] != ""
            and "@" in request.form["email"]
        ):
            user.email = request.form["email"]
        if "power" in request.form and request.form["power"] != "":
            try:
                user.power = int(request.form["power"])
            except Exception as e:
                print(e)
        if "note" in request.form:
            user.note = request.form["note"]
        if "locked" in request.form:
            user.locked = True
        if "locked" not in request.form:
            user.locked = False
        db.session.add(user)
        db.session.commit()
        message = "User modified"
    return render_template("admin_user.html", user=user, message=message)
