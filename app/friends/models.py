from app import db
from datetime import datetime

from app.users.models import User
from app.friends.exceptions import AlreadyFriendsError, ValidationError
from app.friends.exceptions import AlreadyExistsError

class FriendshipRequest(db.Model):
    """Represents friendship request from user to another_user
    """

    __tablename__ = 'friendship_requests'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column('from_user', db.Integer, db.ForeignKey('users.id'))
    to_user = db.Column('to_user', db.Integer, db.ForeignKey('users.id'))

    created_on = db.Column('created_on', db.DateTime,
                           default=datetime.now(), nullable=True)
    rejected_on = db.Column('rejected_on', db.DateTime, nullable=True)
    viewed_on = db.Column('viewed_on', db.DateTime, nullable=True)

    def __init__(self, from_user, to_user):
        self.from_user = from_user
        self.to_user = to_user

        created = datetime.now()

    def accept(self):
        relation1 = Friend(self.from_user, self.to_user)
        relation2 = Friend(self.to_user, self.from_user)

        db.session.add(relation1)
        db.session.add(relation2)

        FriendshipRequest.query.filter_by(
            from_user=self.from_user,
            to_user=self.to_user
        ).delete()

        # delete any reverse requests
        FriendshipRequest.query.filter_by(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        db.session.commit()

    def reject(self):
        """Rejects friendship request"""
        self.rejected_on = datetime.now()
        db.session.add(self)
        db.session.commit()

    def cancel(self):
        """Cancels friendship request"""
        db.session.delete(self)
        db.session.commit()

    def mark_viewed(self):
        """Marks friendship request as viewed"""
        self.viewed_on = datetime.now()
        db.session.add(self)
        db.session.commit()

class FriendshipManager():
    """ Friendship manager """

    def friends(self, user_id):
        """Returns a list of all friends ids"""
        friends = Friend.query.filter_by(to_user=user_id).all()

        users = []
        for friend in friends:
            user = User.query.filter_by(id=friend.from_user).first()
            if user is None:
                continue

            users.append(user)

        return users

    def requests(self, user_id):
        """Return a list of friendship requests"""
        requests = FriendshipRequest.query.filter_by(to_user=user_id).all()
        return requests

    def sent_requests(self, user_id):
        """Returns a list of friendship requests from user"""
        requests = FriendshipRequest.query.filter_by(from_user=user_id).all()
        return requests

    def unread_requests(self, user_id):
        """Returns a list of unread friendship requests"""
        unread_requests = FriendshipRequest.query.filter_by(
            to_user=user_id
        ).all()

        unread_requests = [request for request in unread_requests
                              if request.viewed_on is None]
        return unread_requests

    def unread_request_count(self, user_id):
        """Returns a count of unread friendship requests"""
        return len(self.unread_requests(user_id))

    def read_requests(self, user_id):
        """Returns a list of read friendship requests"""
        read_requests = FriendshipRequest.query.filter_by(to_user=user_id).all()
        read_requests = [request for request in read_requests
                            if request.viewed_on is not None]
        return read_requests

    def rejected_requests(self, user_id):
        """Returns a list of rejected friendship requests"""
        rejected_requests = FriendshipRequest.query.filter_by(
            to_user=user_id
        ).all()

        rejected_requests = [request for request in rejected_requests
                                if request.rejected_on is not None]
        return rejected_requests

    def unrejected_requests(self, user_id):
        """Returns all requests that have not been rejected"""
        requests = FriendshipRequest.query.filter_by(to_user=user_id).all()
        requests = [request for request in requests
                        if request.rejected_on is None]
        return requests

    def unrejected_request_count(self, user_id):
        """Returns a count of unrejected friendship requests"""
        return len(self.unrejected_requests(user_id))

    def make_friends(self, from_user, to_user):
        """Make two users friends"""
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError("Users are already friends")

        # creating new relationship
        relation1 = Friend(from_user, to_user)
        relation2 = Friend(to_user, from_user)

        db.session.add(relation1)
        db.session.add(relation2)

        # deletee all friendship requests
        FriendshipRequest.query.filter_by(
            from_user=from_user,
            to_user=to_user
        ).delete()

        FriendshipRequest.query.filter_by(
            from_user=to_user,
            to_user=from_user
        ).delete()

        db.session.commit()

    def add_friend(self, from_user, to_user):
        """Create a friendship request"""
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError("Users are already friends")

        # checks if friendship request has been already sent
        request = FriendshipRequest.query.filter_by(
            from_user=from_user,
            to_user=to_user
        ).first()

        if request is not None:
            raise AlreadyExistsError("Friendship already requested")

        # if friendship request have not been sent yet, create new
        request = FriendshipRequest(
            from_user=from_user,
            to_user=to_user
        )

        db.session.add(request)
        db.session.commit()

        return request

    def remove_friend(self, from_user, to_user):
        """Destroy a friendship relationship"""
        if not self.are_friends(from_user, to_user):
            return False

        Friend.query.filter_by(to_user=to_user, from_user=from_user).delete()
        Friend.query.filter_by(to_user=from_user, from_user=to_user).delete()

        db.session.commit()
        return True

    def are_friends(self, user1_id, user2_id):
        """Checks if these two users are friends"""
        friends = Friend.query.filter_by(
            to_user=user1_id,
            from_user=user2_id
        ).all()

        return ((friends is not None) and (len(friends) > 0))

class Friend(db.Model):
    """Represents friendship between 2 users
    """

    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column('from_user', db.Integer, db.ForeignKey('users.id'))
    to_user = db.Column('to_user', db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column('created_on', db.DateTime, default=datetime.now())

    objects = FriendshipManager()

    def __init__(self, from_user, to_user):
        self.from_user = from_user
        self.to_user = to_user
