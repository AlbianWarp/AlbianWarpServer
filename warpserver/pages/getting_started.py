from flask import Blueprint, render_template, Response

getting_started_page_blueprint = Blueprint(
    "getting_started", __name__, template_folder="templates"
)


@getting_started_page_blueprint.route("/getting_started", methods=["GET"])
def getting_started():
    return render_template(
        "getting_started.html"
    )
