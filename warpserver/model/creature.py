import sqlalchemy

from .base import db, BaseModel
from .user import User


class Creature(BaseModel):
    """Docsting"""

    __tablename__ = 'creatures'
    name = db.Column(db.String(30))
    uuid = db.Column(db.String(36))
    species = db.Column(db.Integer())
    filename = db.Column(db.String(256))
    sender_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    recipient_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    sender = sqlalchemy.orm.relationship('User', foreign_keys='Creature.sender_user_id', lazy='subquery')
    recipient = sqlalchemy.orm.relationship('User', foreign_keys='Creature.recipient_user_id', lazy='subquery')

    def __init__(self, name, filename, sender_user, recipient_user, uuid):
        self.name = name
        self.uuid = uuid
        self.recipient_user_id = recipient_user.id
        self.sender_user_id = sender_user.id
        self.filename = filename

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': "%s_%s" % (self.uuid, self.filename),
            'species': self.species,
            'uploaded': self.date_created.isoformat("T") + 'Z'
        }
