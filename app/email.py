# -*- coding: utf-8 -*-

from flask.ext.mail import Message
from app import app, mail, celery

# sending email
def send_email(to, subject, template):
    """Sends email with provided info"""
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )

    # send async (celery) email with 10 sec delay
    send_async_email.apply_async(args=[msg], countdown=10)

@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail"""
    with app.app_context():
        mail.send(msg)
