from flask import Blueprint, render_template


tos_page_blueprint = Blueprint("tos", __name__, template_folder="templates")


@tos_page_blueprint.route("/tos", methods=["GET"])
def tos_page():
    return render_template("tos.html")
