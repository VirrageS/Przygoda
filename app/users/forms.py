# -*- coding: utf-8 -*-

from flask_wtf import Form
from flask_babel import gettext
from flask_login import current_user

from wtforms import BooleanField, StringField, PasswordField
from wtforms.validators import Required, EqualTo, Email, Optional, Length
from werkzeug import check_password_hash, generate_password_hash
from app.users.models import User
import re # for checking username

def validate_username_characters(username):
    """Validates username"""
    return username == re.sub("[^a-zA-Z0-9_\.]", "", username)

def validate_username_blocked(username):
    """Checks if username is not blocked"""
    blocked_names = ['admin', 'mod', 'moderator']
    for blocked_name in blocked_names:
        # check if username is substring of blocked name
        if (username.lower() in blocked_name) or (blocked_name in username.lower()):
            return False

    return True

class RequiredIf(Required):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('No field named "%s" in form' % self.other_field_name)

        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class LoginForm(Form):
    email = StringField('Email Address', [Email(), Length(min=6, max=35)])
    password = PasswordField('Password', [Required()])
    remember_me = BooleanField('Remember me', [])

    # def validate(self):
    #     if not Form.validate(self):
    #         return False
    #
    #     # check username and password
    #     user = User.query.filter_by(username=self.username.data).first()
    #     if (user is None) or (not check_password_hash(user.password, self.password.data)):
    #         self.username.errors.append(u'Nie prawidłowe hasło lub nazwa użytkownika')
    #         return False

class RegisterForm(Form):
    username = StringField('Username', [Length(min=4, max=25)])
    email = StringField('Email Address', [Email(), Length(min=6, max=35)])
    password = PasswordField('Password', [Required()])
    confirm = PasswordField(
        'Repeat Password', [
            Required(),
            EqualTo('password', message=gettext(u'Passwords must match.'))
        ]
    )

    def validate(self):
        if not Form.validate(self):
            return False

        # check if username has valid characters
        if not validate_username_characters(self.username.data):
            self.username.errors.append(gettext(u'Username contains illegal characters.'))
            return False

        if not validate_username_blocked(self.username.data):
            self.username.errors.append(gettext(u'Username is blocked.'))
            return False

        # check username
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append(gettext(u'Username is already in use.'))
            return False

        # email check
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user is not None:
            self.email.errors.append(gettext(u'Email is already in use.'))
            return False

        return True

class AccountForm(Form):
    username = StringField('Username', [Length(min=4, max=25)])
    email = StringField('Email Address', [Email(), Length(min=6, max=35)])
    password = PasswordField('Password', [Optional()])
    confirm = PasswordField(
        'Repeat Password', [
            Optional(),
            EqualTo('password', message=gettext(u'Passwords must match.'))
        ]
    )
    old_password = PasswordField('Old Password', [RequiredIf('password')])

    def validate(self):
        if not Form.validate(self):
            return False

        # check if username has valid characters
        if not validate_username_characters(self.username.data):
            self.username.errors.append(gettext(u'Username contains illegal characters.'))
            return False

        if not validate_username_blocked(self.username.data):
            self.username.errors.append(gettext(u'Username is blocked.'))
            return False

        # check username
        user = User.query.filter_by(username=self.username.data).first()
        if (user is not None) and (user.id != current_user.id):
            self.username.errors.append(gettext(u'Username is already in use.'))
            return False

        # email check
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if (user is not None) and (user.id != current_user.id):
            self.email.errors.append(gettext(u'Email is already in use.'))
            return False

        # check old password
        if ((self.old_password.data is not None) and self.old_password.data
                and (not check_password_hash(current_user.password, self.old_password.data))):
            self.old_password.errors.append(gettext(u'Old password is not correct.'))
            return False

        return True

class LostForm(Form):
    email = StringField('Email Address', [Email(), Length(min=6, max=35)])

    def validate(self):
        if not Form.validate(self):
            return False

        # email check
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user is None:
            self.email.errors.append(gettext(u'Email is not correct.'))
            return False

        if not user.confirmed:
            self.email.errors.append(gettext(u'User with this email is not confirmed.'))
            return False

        return True

class ChangePasswordForm(Form):
    password = PasswordField('Password', [Required()])
    confirm = PasswordField(
        'Repeat Password', [
            Required(),
            EqualTo('password', message=gettext(u'Passwords must match.'))
        ]
    )
