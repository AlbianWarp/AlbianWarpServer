from flask import Blueprint, render_template, Response
from warpserver.config import REBABEL_PORT, REBABEL_CONFIG_HOST, REBABEL_SERVER_NAME

getting_started_page_blueprint = Blueprint(
    "getting_started", __name__, template_folder="templates"
)


@getting_started_page_blueprint.route("/getting_started", methods=["GET"])
def getting_started():
    return render_template(
        "getting_started.html",
        server_name=REBABEL_SERVER_NAME,
        host=REBABEL_CONFIG_HOST,
        port=REBABEL_PORT,
    )


@getting_started_page_blueprint.route("/server.cfg", methods=["GET"])
def server_cfg():
    return Response(
        render_template(
            "server.cfg",
            server_name=REBABEL_SERVER_NAME,
            host=REBABEL_CONFIG_HOST,
            port=REBABEL_PORT,
        ),
        mimetype="text/cfg",
        headers={"Content-disposition": "attachment; filename=server.cfg"},
    )
