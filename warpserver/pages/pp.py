from flask import Blueprint, render_template


pp_page_blueprint = Blueprint('pp', __name__, template_folder='templates')


@pp_page_blueprint.route('/privacy_policy', methods=['GET'])
def pp_page():
    return render_template('pp.html')
