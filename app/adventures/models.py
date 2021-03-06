from app import db
from app.adventures import constants as ADVENTURES
from app.adventures.exceptions import AlreadyParticipantError

from datetime import datetime
from app.users.models import User

class AdventureManager():
    """Adventure manager"""

    def adventures(self):
        """Returns a list of all adventures"""
        adventures = Adventure.query.all()
        return adventures

    def active_adventures(self):
        """Returns a list of all active adventures"""
        adventures = Adventure.query.all()
        adventures = [adventure
                      for adventure in adventures if adventure.is_active()]
        return adventures

    def user_adventures(self, user_id):
        """Returns a list of all adventures created by specific user"""
        adventures = Adventure.query.filter_by(creator_id=user_id).all()
        return adventures

    def user_active_adventures(self, user_id):
        """Returns a list of all active adventures created by specific user"""
        adventures = Adventure.query.filter_by(creator_id=user_id).all()
        adventures = [adventure
                      for adventure in adventures if adventure.is_active()]
        return adventures

    def user_joined_adventures(self, user_id):
        adventure_participated = AdventureParticipant.query.filter_by(
            user_id=user_id).all()

        all_adventures = []
        for participant in adventure_participated:
            if not participant.is_active():
                continue

            # get adventure in which user participated
            adv = Adventure.query.filter_by(id=participant.adventure_id).first()
            if adv is not None:
                all_adventures.append(adv)

        return all_adventures

    def user_joined_active_adventures(self, user_id):
        adventures = self.user_joined_adventures(user_id)
        adventures = [adventure
                      for adventure in adventures
                      if adventure.is_active()]
        return adventures

    def coordinates(self, adventure_id):
        coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
        return coordinates

    def participants(self, adventure_id):
        participants = AdventureParticipant.query.filter_by(
            adventure_id=adventure_id
        ).all()

        users = []
        for participant in participants:
            user = User.query.filter_by(id=participant.user_id).first()
            if user is not None:
                users.append(user)

        return users

    def active_participants(self, adventure_id):
        participants = AdventureParticipant.query.filter_by(
            adventure_id=adventure_id
        ).all()

        participants = [participant
                        for participant in participants
                        if participant.is_active()]

        users = []
        for participant in participants:
            user = User.query.filter_by(id=participant.user_id).first()
            if user is not None:
                users.append(user)

        return users

    def add_participant(self, adventure_id, user_id):
        """Adds user as participant to adventure"""
        # NOTE: should we check if adventure is active and exists?

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure_id,
            user_id=user_id
        ).first()

        # check if participant is in this adventure
        if participant is None:
            participant = AdventureParticipant(
                adventure_id=adventure_id,
                user_id=user_id
            )

            db.session.add(participant)
            db.session.commit()
            return True

        # check if participant is active (we cannot add them one more time)
        if participant.is_active():
            raise AlreadyParticipantError("User is arleady participant")

        participant.left_on = None
        participant.joined_on = datetime.now()
        db.session.add(participant)
        db.session.commit()
        return True

    def remove_participant(self, adventure_id, user_id):
        """Removes user as participant from adventure"""
        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure_id,
            user_id=user_id
        ).first()

        # checks if user is already no longer adventure participant
        if (participant is None) or (not participant.is_active()):
            return False

        participant.left_on = datetime.now()
        db.session.commit()
        return True

class Adventure(db.Model):
    """
    Provides class model for Adventure

    Adventure is a main class in system which represents all
    necessary infomartions about

    """

    __tablename__ = 'adventures'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column('creator_id', db.Integer, db.ForeignKey('users.id'))
    date = db.Column('date', db.DateTime)
    mode = db.Column('mode', db.SmallInteger, nullable=False,
                     default=ADVENTURES.RECREATIONAL)
    info = db.Column('info', db.String, nullable=False, default='')
    created_on = db.Column('created_on', db.DateTime)
    disabled = db.Column('disabled', db.Boolean, nullable=False, default=False)
    disabled_on = db.Column('disabled_on', db.DateTime, nullable=True)
    deleted = db.Column('deleted', db.Boolean, nullable=False, default=False)
    deleted_on = db.Column('deleted_on', db.DateTime, nullable=True)

    objects = AdventureManager()

    def __init__(self, creator_id, date, mode, info):
        self.creator_id = creator_id
        self.date = date
        self.mode = mode
        self.info = info
        self.created_on = datetime.now()
        self.disabled = False
        self.deleted = False

    def get_mode(self):
        """Returns mode of adventure"""
        return ADVENTURES.MODES[self.mode]

    def is_active(self):
        """Checks if adventure is active"""
        return ((not self.deleted) and (self.date >= datetime.now())
                and (not self.disabled))

    def get_participants(self):
        """Returns active participants of the adventure"""
        participants = AdventureParticipant.query.filter_by(
            adventure_id=self.id
        ).all()

        participants = [participant for participant in participants
                            if participant.is_active()]
        return participants


class Coordinate(db.Model):
    __tablename__ = 'coordinates'
    id = db.Column(db.Integer, primary_key=True)
    adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
    path_point = db.Column('path_point', db.Integer)
    latitude = db.Column('latitude', db.Float)
    longitude = db.Column('longitude', db.Float)

    def __init__(self, adventure_id, path_point, latitude, longitude):
        self.adventure_id = adventure_id
        self.path_point = path_point
        self.latitude = latitude
        self.longitude = longitude


class AdventureParticipant(db.Model):
    __tablename__ = 'adventure_participants'
    id = db.Column(db.Integer, primary_key=True)
    adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    joined_on = db.Column('joined_on', db.DateTime, nullable=True)
    left_on = db.Column('left_on', db.DateTime, nullable=True)

    def __init__(self, adventure_id, user_id):
        self.adventure_id = adventure_id
        self.user_id = user_id
        self.joined_on = datetime.now()

    def is_active(self):
        """Checks if participant of adventure is still active"""
        return (self.left_on is None)
