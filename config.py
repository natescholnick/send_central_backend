import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    SECRET_KEY = 'this-is-a-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:pass@localhost:5432/sendcentral'

    MAIL_PASSWORD = 'suldjynyahuyidur'
    MAIL_USERNAME = 'sendcentralteam@gmail.com'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_USE_TLS = 1
    MAIL_PORT = 587
    ADMINS = ['sendcentralteam@gmail.com']
