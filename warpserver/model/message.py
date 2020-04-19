import sqlalchemy

from .base import db, BaseModel
from .user import User


class Message(BaseModel):
    """Docsting"""

    __tablename__ = "messages"
    data = db.Column(db.Text())
    sender_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    recipient_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    sender = sqlalchemy.orm.relationship(
        "User", foreign_keys="Message.sender_user_id", lazy="subquery"
    )
    recipient = sqlalchemy.orm.relationship(
        "User", foreign_keys="Message.recipient_user_id", lazy="subquery"
    )

    def __init__(self, recipient, sender, data):
        self.recipient_user_id = recipient.id
        self.sender_user_id = sender.id
        self.data = data

    def __repr__(self):
        return "<Message #%s>" % self.id

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "sender": self.sender.to_dict(),
            "recipient": self.recipient.to_dict(),
            "created": self.date_created.isoformat("T") + "Z",
        }
