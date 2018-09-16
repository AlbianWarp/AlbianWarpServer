from warpserver.util import admin_required, token_required
from flask import Blueprint, render_template, session

from warpserver.model.base import db

from warpserver.model import User

admin_page_blueprint = Blueprint('admin', __name__,
                                    template_folder='templates')


@admin_page_blueprint.route('/admin', methods=['GET'])
@token_required
@admin_required
def admin_overview():
    return render_template('admin_overview.html', session=session)


@admin_page_blueprint.route('/admin_user', methods=['GET'])
@token_required
@admin_required
def admin_user():
    users = db.session.query(User).all()
    users_dict  = []
    for user in users:
        users_dict.append({'id': user.id, 'name': user.username, 'email': user.email, 'power': user.power})
    return render_template('admin_user.html', users=users, session=session)

