import datetime
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()


class User(Base):
    """Docsting"""

    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    username = sqlalchemy.Column(sqlalchemy.String(30), unique=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String())
    email = sqlalchemy.Column(sqlalchemy.String())

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
        return {'username': self.username,
                'id': self.id,
                'created': self.created.isoformat("T") + 'Z'}


class Message(Base):
    """Docsting"""

    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    data = sqlalchemy.Column(sqlalchemy.String())

    sender_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id))
    recipient_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id))
    sender = sqlalchemy.orm.relationship('User', foreign_keys='Message.sender_user_id', lazy='subquery')
    recipient = sqlalchemy.orm.relationship('User', foreign_keys='Message.recipient_user_id', lazy='subquery')

    def __init__(self, recipient, sender, data):
        self.recipient_user_id = recipient.id
        self.sender_user_id = sender.id
        self.data = data

    def __repr__(self):
        return '<Message #%s>' % self.id

    def to_dict(self):
        return {'id': self.id,
                'data': self.data,
                'sender': self.sender.to_dict(),
                'recipient': self.recipient.to_dict(),
                'created': self.created.isoformat("T") + 'Z'}


class Creature(Base):
    """Docsting"""

    __tablename__ = 'creatures'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    uploaded = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    name = sqlalchemy.Column(sqlalchemy.String(30), unique=True)
    species = sqlalchemy.Column(sqlalchemy.String())
    sender_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id))
    recipient_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id))
    sender = sqlalchemy.orm.relationship('User', foreign_keys='Creature.sender_user_id', lazy='subquery')
    recipient = sqlalchemy.orm.relationship('User', foreign_keys='Creature.recipient_user_id', lazy='subquery')

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def to_dict(self):
        return {'creaturename': self.name,
                'species': self.species,
                'id': self.id,
                'uploaded': self.uploaded.isoformat("T") + 'Z'}
