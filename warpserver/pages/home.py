from flask import Blueprint, render_template


home_page_blueprint = Blueprint('home', __name__, template_folder='templates')


@home_page_blueprint.route('/', methods=['GET'])
@home_page_blueprint.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')
