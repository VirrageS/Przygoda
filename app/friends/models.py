from app import db
from datetime import datetime

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
        relation2 = Friend(self.from_user, self.to_user)

        db.session.add(relation1)
        db.session.add(relation2)

        self.delete()

        # delete any reverse requests
        FriendshipRequest.query.filter_by(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        db.session.commit()

    def reject(self):
        """Rejects friendship request"""
        self.rejected = datetime.now()
        db.session.add(self)
        db.session.commit()

    def cancel(self):
        """Cancels friendship request"""
        self.delete()
        db.session.commit()

    def mark_viewed(self):
        """Marks friendship request as viewed"""
        self.viewed = datetime.now()
        db.session.add(self)
        db.session.commit()

class FriendshipManager():
    """ Friendship manager """

    def friends(self, user):
        """ Return a list of all friends """
        qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
        friends = [u.from_user for u in qs]
        return friends

    def requests(self, user):
        """ Return a list of friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user).all()
        requests = list(qs)
        return requests

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        requests = FriendshipRequest.query.filter_by(from_user=user).all()
        return requests

    def unread_requests(self, user):
        """ Return a list of unread friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=True).all()
        unread_requests = list(qs)
        return unread_requests

    def unread_request_count(self, user):
        """ Return a count of unread friendship requests """
        count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=True).count()
        return count

    def read_requests(self, user):
        """ Return a list of read friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=False).all()
        read_requests = list(qs)
        return read_requests

    def rejected_requests(self, user):
        """ Return a list of rejected friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            rejected__isnull=False).all()
        rejected_requests = list(qs)
        return rejected_requests

    def unrejected_requests(self, user):
        """ All requests that haven't been rejected """
        key = cache_key('unrejected_requests', user.pk)
        unrejected_requests = cache.get(key)

        if unrejected_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                rejected__isnull=True).all()
            unrejected_requests = list(qs)
            cache.set(key, unrejected_requests)

        return unrejected_requests

    def unrejected_request_count(self, user):
        """ Return a count of unrejected friendship requests """
        count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            rejected__isnull=True).count()
        return count

    def add_friend(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError("Users are already friends")

        if message is None:
            message = ''

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
        )

        if created is False:
            raise AlreadyExistsError("Friendship already requested")

        if message:
            request.message = message
            request.save()

        bust_cache('requests', to_user.pk)
        bust_cache('sent_requests', from_user.pk)
        friendship_request_created.send(sender=request)

        return request

    def remove_friend(self, to_user, from_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user) |
                Q(to_user=from_user, from_user=to_user)
            ).distinct().all()

            if qs:
                friendship_removed.send(
                    sender=qs[0],
                    from_user=from_user,
                    to_user=to_user
                )
                qs.delete()
                bust_cache('friends', to_user.pk)
                bust_cache('friends', from_user.pk)
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        try:
            Friend.objects.get(to_user=user1, from_user=user2)
            return True
        except Friend.DoesNotExist:
            return False

class Friend(db.Model):
    """Represents friendship between 2 users
    """

    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column('from_user', db.Integer, db.ForeignKey('users.id'))
    to_user = db.Column('to_user', db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column('created_on', db.DateTime, default=datetime.now())

    def __init__(self, from_user, to_user):
        self.from_user = from_user
        self.to_user = to_user
        self.created_on = created_on

    def save(self, *args, **kwargs):
        # Ensure users cannot be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")

        super(Friend, self).save(*args, **kwargs)
