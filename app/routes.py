from app import app, db
from flask import jsonify, request, redirect, url_for
from app.models import User, Gym, Climb
from flask_login import login_user, logout_user, login_required, current_user
import datetime
import time
import jwt


@app.route('/')
def index():
  return "Send Central API"


@app.route('/api/register', methods=['GET', 'POST'])
def register():
  try:
    token = request.headers.get('token')
    data = jwt.decode(
      token,
      app.config['SECRET_KEY'],
      algorithm=['HS256']
    )
    print(data)


    user = User(
      first_name = data['first_name'],
      last_name = data['last_name'],
      display_name = data['display_name'],
      birthdate = data['birthdate'],
      email = data['email'],
      date_created = datetime.now()
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'code' : 201, 'message' : 'Account registered successfully.'})

  except:
    return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


@app.route('/api/login', methods=['GET', 'POST'])
def login():
  try:
    token = request.headers.get('token')
    data= jwt.decode(
      token,
      app.config['SECRET_KEY'],
      algorithm=['HS256']
    )

    user = User.query.filter_by(email=data['email']).first()

    if user is None or not user.check_password(data['password']):
      return jsonify({ 'code' : 401, 'message' : 'Invalid credentials.' })

    return jsonify({ 'code' : 200, 'message' : 'Login successful.', 'token': user.get_token()})

  except:
    return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


