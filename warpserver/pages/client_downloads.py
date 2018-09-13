from flask import Blueprint, render_template, jsonify


import requests
from warpserver.util import memoized_ttl
from warpserver.config import CLIENT_GITHUB_API_URL

client_downloads_page_blueprint = Blueprint('client_download', __name__, template_folder='templates')


@memoized_ttl(3600)
def get_latest_client_release_information_from_github():
    r = requests.get('%s/releases/latest' % CLIENT_GITHUB_API_URL)
    if r.status_code == 200:
        return r.json()

@memoized_ttl(7200)
def get_client_release_informations_from_github():
    r = requests.get('%s/releases' % CLIENT_GITHUB_API_URL)
    if r.status_code == 200:
        return r.json()


@client_downloads_page_blueprint.route('/client_downloads', methods=['GET'])
def downloads_page():
    return render_template('client_downloads.html', latest_release=get_latest_client_release_information_from_github(), releases=get_client_release_informations_from_github())

@client_downloads_page_blueprint.route('/client_latest.json', methods=['GET'])
def client_latest():
    return jsonify(get_latest_client_release_information_from_github())

@client_downloads_page_blueprint.route('/client_releases.json', methods=['GET'])
def client_releases():
    return jsonify(get_client_release_informations_from_github())