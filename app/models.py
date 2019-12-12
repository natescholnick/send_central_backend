from app import app, db, login
from datetime import datetime
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(50))
    display_name = db.Column(db.String(50), unique=True, index=True)
    birthdate = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, index=True)
    bio = db.Column(db.Text)
    prof_img_url = db.Column(db.String(250), default='http://placehold.it/250x250')
    password_hash = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)
    last_logged_in = db.Column(db.DateTime)
    # posts = db.relationship('Post', backref=db.backref('user', lazy='joined'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    def convert_to_seconds(s):
        return int(s[:-1]) * seconds_per_unit[s[-1]]

    def get_token(self, expires_in='10m'):
        return jwt.encode(
            { 'user_id': self.id, 'exp': time() + convert_to_seconds(expires_in) },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithm=['HS256']
            )['user_id']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f'<User {self.id}: {self.email}>'



class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    display_name = db.Column(db.String(50), unique=True, index=True)
    address = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(15))
    external_url = db.Column(db.String(150))
    gym_img_url = db.Column(db.String(250), default='http://placehold.it/250x250')
    date_created = db.Column(db.DateTime)
    description = db.Column(db.Text)


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    climb_name = db.Column(db.String(100))
    climb_type = db.Column(db.String(15))
    grade = db.Column(db.String(8))
    color = db.Column(db.String(20))
    station = db.Column(db.String(20))
    date_set = db.Column(db.Date)
    date_stripped = db.Column(db.Date)
    setter = db.Column(db.String(30))
    user_id = db.Column(db.Integer)
    climb_img_url = db.Column(db.String(250), default='http://placehold.it/250x250')


class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    notes = db.Column(db.String(300))
    date_created = db.Column(db.Date)


class Send(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    climb_id = db.Column(db.Integer)
    training_id = db.Column(db.Integer)
    send_category = db.Column(db.String(15))
    notes = db.Column(db.String(150))
    time_created = db.Column(db.Time)
    media_url = db.Column(db.String(256))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
