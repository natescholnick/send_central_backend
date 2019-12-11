from flask_mail import Message
from app import app, mail
from flask import render_template


def registrationMail(token, email):
    msg = Message(
        subject = 'Complete your Registration for Send Central!',
        sender = app.config['ADMINS'][0],
        recipients = [email]
    )

    msg.body = render_template('email/registration.txt', token=token)

    msg.html = render_template('email/registration.html', token=token)

    mail.send(msg)

def resetPasswordMail(token, email):
    msg = Message(
        subject = 'Follow the Link Provided to Reset your Password!',
        sender = app.config['ADMINS'][0],
        recipients = [email]
    )

    msg.body = render_template('email/password_reset.txt', token=token)

    msg.html = render_template('email/password_reset.html', token=token)

    mail.send(msg)
