import re

from flask import Blueprint, request, render_template, session, redirect

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.fields.html5 import EmailField

from warpserver.model.base import db
from warpserver.model import User

login_page_blueprint = Blueprint('login', __name__,
                                    template_folder='templates')



class LoginForm(FlaskForm):

    username = StringField(
           'Enter Username',
                            validators=[DataRequired()])
    password = PasswordField('Enter password',
                             validators=[DataRequired()])


@login_page_blueprint.route('/login', methods=['POST', 'GET'])
def login_form():
    form = LoginForm()
    message = None
    success = False
    if request.method == 'POST':
        if form.validate_on_submit():
            message = "Login failed!"
            user = db.session.query(User).filter(User.username == request.form['username']).first()
            if user:
                if user.check_password(request.form['password']):
                    session['logged_in'] = True
                    session['user_id'] = user.id
                    session['user_name'] = user.username
                    return redirect("/home")

    return render_template('login.html', form=form, message=message, success=success, session=session)

@login_page_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("/login")

