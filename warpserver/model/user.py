from werkzeug.security import generate_password_hash, check_password_hash

from .base import db, BaseModel


class User(BaseModel):
    """Docsting"""

    __tablename__ = 'users'
    username = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String())
    email = db.Column(db.String())
    power = db.Column(db.Integer())

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = self.hash_password(password)
        self.email = email

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }
