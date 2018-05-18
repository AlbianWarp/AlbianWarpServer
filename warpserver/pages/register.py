import re

from flask import Blueprint, request, render_template

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.fields.html5 import EmailField

from warpserver.model.base import db
from warpserver.model import User

register_page_blueprint = Blueprint('register', __name__,
                                    template_folder='templates')


class Unique(object):
    def __init__(self, model, field, message=u'This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class UsernameCharacterValidator(object):
    def __init__(self, re_pattern, message=u"Field contained invalid characters!"):
        self.pattern = re.compile(re_pattern)
        self.message = message

    def __call__(self, form, field):
        if bool(self.pattern.search(field.data)):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    email = EmailField('Enter email',
                       validators=[
                           DataRequired(),
                           Email()
                       ])
    email_confirmation = EmailField('Repeat email',
                                    validators=[DataRequired(),
                                                Email(),
                                                EqualTo('email', message='email must match')
                                                ])
    username = StringField('Enter Username',
                           validators=[
                               DataRequired(),
                               Length(min=3, max=18),
                               Unique(User, User.username, message="User Already exists!"),
                               UsernameCharacterValidator(
                                   re_pattern=r'[^a-zA-Z0-9]',
                                   message=u'Username contains invalid characters Only "a-z, A-Z, 0-9" are allowed'
                               )
                           ])
    password = PasswordField('Enter password',
                             validators=[
                                 DataRequired(),
                                 Length(min=8)
                             ])
    password_confirmation = PasswordField('Repeat password',
                                          validators=[
                                              DataRequired(),
                                              Length(min=8),
                                              EqualTo('password', message='password must match')
                                          ])


@register_page_blueprint.route('/register', methods=['POST', 'GET'])
def register_form():
    form = RegistrationForm()
    message = None
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(username=request.form['username'], password=request.form['password'],
                            email=request.form['email'])
            db.session.add(new_user)
            db.session.commit()
            message = "User successfully created!"
    return render_template('register.html', form=form, message=message)
