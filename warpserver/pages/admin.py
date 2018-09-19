from warpserver.util import api_admin_required, api_token_required
from flask import Blueprint, render_template, session

from warpserver.model.base import db

from warpserver.model import User

admin_page_blueprint = Blueprint('admin', __name__,
                                    template_folder='templates')


@admin_page_blueprint.route('/admin', methods=['GET'])
@api_token_required
@api_admin_required
def admin_overview():
    return render_template('admin_dashboard.html', session=session)


@admin_page_blueprint.route('/admin/user', methods=['GET'])
@api_token_required
@api_admin_required
def admin_user():
    users = db.session.query(User).all()
    users_dict  = []
    for user in users:
        users_dict.append({'id': user.id, 'name': user.username, 'email': user.email, 'power': user.power})
    return render_template('admin_user_overview.html', users=users, session=session)

