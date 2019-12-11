from app import app, db
from flask import jsonify, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
import jwt
from datetime import datetime
import time
from app.models import User, Gym, Climb
from app.email import registrationMail, resetPasswordMail


@app.route('/')
def index():
  return "Send Central API"


###################
### ACCOUNT API ###
###################

@app.route('/api/account/change-password', methods=['GET', 'POST'])
def change_password():
    try:
        token = request.headers.get('token')
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        user = User.query.get(data['user_id'])

        if not user.check_password(data['password']):
            return jsonify({ 'code' : 401, 'message' : 'Incorrect password.' })

        else:
            user.set_password(data['new_password'])
            return jsonify({ 'code' : 200, 'message' : 'Password changed successfully.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})


@app.route('/api/account/delete', methods=['DELETE'])
def delete_account():
    try:
        user_id = request.headers.get('user_id')

        user = User.query.get(user_id)

        db.session.delete(user)
        db.session.commit()

        return jsonify({ 'code' : 200, 'message' : 'Account deleted.' })

    except:
        return jsonify({ 'code' : 401, 'message' : 'No account found.' })


@app.route('/api/account/login', methods=['GET', 'POST'])
def login():
  try:
    token = request.headers.get('token')
    data = jwt.decode(
      token,
      app.config['SECRET_KEY'],
      algorithm=['HS256']
    )

    user = User.query.filter_by(email=data['email']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({ 'code' : 401, 'message' : 'Invalid credentials.' })

    user.last_logged_in = datetime.now()
    db.session.commit()

    return jsonify({ 'code' : 200, 'message' : 'Login successful.', 'token': user.get_token(expires_in='52w')})

  except:
    return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


@app.route('/api/account/register', methods=['GET', 'POST'])
def register():
  try:
    token = request.args.get('token')
    print(token)
    data = jwt.decode(
      token,
      app.config['SECRET_KEY'],
      algorithm=['HS256']
    )
    print(data)

    birthdate_str = data['birthdate']
    birthdate_obj = datetime.strptime(birthdate_str, '%Y-%m-%d').date()

    user = User(
      first_name = data['first_name'],
      last_name = data['last_name'],
      display_name = data['display_name'],
      birthdate = birthdate_obj,
      email = data['email'],
      date_created = datetime.now()
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'code' : 201, 'message' : 'Account registered successfully.'})

  except:
    return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


@app.route('/api/account/reset-password', methods=['GET', 'POST'])
def reset_password():
    try:
        token = request.headers.get('token')
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        user = User.query.get(data['user_id'])

        if data['forgot_password'] == True:
            user.set_password(data['new_password'])
            return jsonify({ 'code' : 200, 'message' : 'Password changed successfully.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})


#################
### CLIMB API ###
#################

@app.route('/api/climb/create', methods=['POST'])
def create_climb():
    try:
        climbs_list = request.headers.get('climbs_list')
        to_commit = []
        for element in climbs_list:
            date_set_str = element['date_set']
            date_set_obj = datetime.strptime(date_set_str, '%Y-%m-%d').date()

            climb = Climb(
                climb_name = element['climb_name'],
                climb_type = element['climb_type'],
                grade = element['grade'],
                color = element['color'],
                station = element['station'],
                date_set = element['date_set_obj'],
                setter = element['setter'],
                user_id = element['user_id'],
            )

            # TODO: pass image to backend, save to disk, generate image file path

            db.session.add(climb)

        db.session.commit()

        return jsonify({'code' : 201, 'message' : 'Climb(s) created successfully.'})

    except:
        return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


###############
### GYM API ###
###############

@app.route('/api/climb/create', methods=['POST'])
def create_gym():
    try:

        gym = Gym(
            full_name = request.headers.get('full_name'),
            display_name = request.headers.get('display_name'),
            address = request.headers.get('address'),
            email = request.headers.get('email'),
            phone = request.headers.get('phone'),
            external_url = request.headers.get('external_url'),
            date_created = datetime.now(),
            description = request.headers.get('description')
        )

        db.session.add(gym)
        db.session.commit()

        return jsonify({'code' : 201, 'message' : 'Gym page created successfully.'})

    except:
        return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


################
### MAIL API ###
################

@app.route('/api/mail/registration', methods=['GET'])
def sendRegistration():
    try:
        token = request.headers.get('token')
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        registrationMail(token, data['email'])
        return jsonify({ 'code': 200, 'message': 'Registration email sent successfully. Follow the link in the email within 10 minutes to complete registration.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong'})


@app.route('/api/mail/reset_password', methods=['GET'])
def sendPasswordReset():
    try:
        token = request.headers.get('token')
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        user = User.query.filter_by(email=data['email']).first()

        if user == None:
            return jsonify ({'code': 401, 'messasge': 'No user found associated with this email address.'})

        else:
            token_out = jwt.encode(
                { 'user_id': user.id, 'forgot_password': True, 'exp': time() + 600},
                app.config['SECRET_KEY'],
                algorithm='HS256'
            ).decode('utf-8')
            resetPasswordMail(token_out, data['email'])
            return jsonify({ 'code': 200, 'message': 'Registration email sent successfully. Follow the link in the email within 10 minutes to complete registration.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong'})
