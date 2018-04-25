from flask import Blueprint, request

from warpserver.model.base import db
from warpserver.model import User

register_page = Blueprint('register', __name__,
                          template_folder='templates')


@register_page.route('/register', methods=['POST', 'GET'])
def register_form():
    if request.method == 'POST':
        user = db.session.query(User).filter(User.username == request.form['username']).first()
        if user:
            return '<h1>THAT USER ALREADY EXISTS!!!!</h1>', 409
        new_user = User(username=request.form['username'], password=request.form['password'],
                        email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return '<h1>USER CREATED!</h1>'
    return """
<form name="register_form"  method="POST">
email: <input type="text" name="email">
<br /> username: <input type="text" name="username">
<br /> password: <input type="password" name="password">
<br /> <input type="submit" value="Submit">
</form>
"""
