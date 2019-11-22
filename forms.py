from app import app, db
from app.models import User
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class PostForm(FlaskForm):
    tweet = StringField('What\'s on your mind?', validators=[DataRequired(), Length(max=140)])
    submit = SubmitField('Tweet')

class TitleForm(FlaskForm):
    title = StringField('Enter a new header:', validators=[DataRequired()])
    submit = SubmitField('Change Title')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    age = StringField('Age')
    bio = StringField('Bio')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Re-Type Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # setup validation methods to be checked when form is submitted
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            flash('Invalid username.')
            raise ValidationError('Invalid username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            flash('Invalid email')
            raise ValidationError('Invalid email')
