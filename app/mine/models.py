from app import db
from datetime import datetime

class AdventureSearches(db.Model):
    __tablename__ = 'adventure_searches'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
    date = db.Column('date', db.DateTime)
    value = db.Column('value', db.Integer)

    def __init__(self, user_id, adventure_id, value=1):
        self.user_id = user_id
        self.adventure_id = adventure_id
        self.date = datetime.now()
        self.value = value


class AdventureViews(db.Model):
    __tablename__ = 'adventure_views'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
    date = db.Column('date', db.DateTime)
    value = db.Column('value', db.Integer)

    def __init__(self, user_id, adventure_id, value=1):
        self.user_id = user_id
        self.adventure_id = adventure_id
        self.date = datetime.now()
        self.value = value

class UserReports(db.Model):
    __tablename__ = 'user_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column('email', db.String, nullable=True, default='')
    subject = db.Column('subject', db.String, nullable=True, default='')
    message = db.Column('message', db.String, nullable=True, default='')
    display = db.Column('display', db.Boolean, nullable=False, default=True)
    created_on = db.Column('created_on', db.DateTime)

    def __init__(self, user_id, email, subject, message):
        self.user_id = user_id
        self.email = email
        self.subject = subject
        self.message = message
        self.created_on = datetime.now()
        self.display = True
