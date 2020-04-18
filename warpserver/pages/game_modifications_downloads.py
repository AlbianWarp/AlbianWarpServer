from flask import Blueprint, render_template, jsonify


import requests
from warpserver.util import MemoizedTTL
from warpserver.config import GAME_MODIFICATIONS_GITHUB_API_URL

game_modifications_downloads_page_blueprint = Blueprint(
    "game_modifications_download", __name__, template_folder="templates"
)


@MemoizedTTL(3600)
def get_latest_game_modifications_release_information_from_github():
    r = requests.get("%s/releases/latest" % GAME_MODIFICATIONS_GITHUB_API_URL)
    if r.status_code == 200:
        return r.json()


@MemoizedTTL(7200)
def get_game_modifications_release_informations_from_github():
    r = requests.get("%s/releases" % GAME_MODIFICATIONS_GITHUB_API_URL)
    if r.status_code == 200:
        return r.json()


@game_modifications_downloads_page_blueprint.route(
    "/game_modifications_downloads", methods=["GET"]
)
def downloads_page():
    return render_template(
        "game_modifications_downloads.html",
        latest_release=get_latest_game_modifications_release_information_from_github(),
        releases=get_game_modifications_release_informations_from_github(),
    )


@game_modifications_downloads_page_blueprint.route(
    "/game_modifications_latest.json", methods=["GET"]
)
def game_modifications_latest():
    return jsonify(get_latest_game_modifications_release_information_from_github())


@game_modifications_downloads_page_blueprint.route(
    "/game_modifications_releases.json", methods=["GET"]
)
def game_modifications_releases():
    return jsonify(get_game_modifications_release_informations_from_github())
