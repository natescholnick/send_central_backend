from app import app, db
from flask import jsonify, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
import jwt
from datetime import datetime
import time
from app.models import User, Gym, Climb, Training, Send
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

        if not user or not user.check_password(data['password']):
            return jsonify({ 'code' : 401, 'message' : 'Invalid credentials.' })

        else:
            user.set_password(data['new_password'])
            db.session.commit()
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
    data = jwt.decode(
      token,
      app.config['SECRET_KEY'],
      algorithm=['HS256']
    )

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


#################
### CLIMB API ###
#################

@app.route('/api/climb/create', methods=['POST'])
def create_climbs():
    # try:
        climbs_list = request.headers.get('climbs_list')
        print(climbs_list[0:10])
        to_commit = []
        for element in climbs_list:
            date_set_str = element['date_set']
            date_set_obj = datetime.strptime(date_set_str, '%Y-%m-%d').date()

            climb = Climb(
                gym_id = element['gym_id'],
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

    # except:
        return jsonify({ 'code' : 400, 'message' : 'Something went wrong.'})


@app.route('/api/climb/get_climbs', methods=['GET'])
def get_climbs():
    try:
        climbs = Climb.query.all()
        climb_dicts = []

        for climb in climbs:
            climb_dict = {
                'id': climb.id,
                'climb_name': climb.climb_name,
                'climb_type': climb.climb_type,
                'grade': climb.grade,
                'color': climb.color,
                'station': climb.station,
                'date_set': climb.date_set,
                'setter': climb.setter,
                'user_id': climb.user_id,
                'climb_img_url': climb.climb_img_url
                # TODO: Add query for climb rating! Also make view in SQL!
            }
            climb_dicts.append(climb_dict)

        return jsonify({'code': 200, 'message': 'Query successful', 'climbs': climb_dicts})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})


###############
### GYM API ###
###############

@app.route('/api/gym/create', methods=['POST'])
def create_gym():
    try:
        gym = Gym(
            full_name = request.headers.get('full_name'),
            display_name = request.headers.get('display_name'),
            address = request.headers.get('address'),
            city = request.headers.get('city'),
            country = request.headers.get('country'),
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


@app.route('/api/gym/get_gyms', methods=['GET'])
def get_gyms():
    try:
        gyms = Gym.query.all()
        gym_dicts = []

        for gym in gyms:
            gym_dict = {
                'id': gym.id,
                'full_name': gym.full_name,
                'display_name': gym.display_name,
                'address': gym.address,
                'city': gym.city,
                'country': gym.country,
                'email': gym.email,
                'phone': gym.phone,
                'external_url': gym.external_url,
                'gym_img_url': gym.gym_img_url,
                'date_created': gym.date_created,
                'description': gym.description
                # TODO: Add query for gym rating! Also make view in SQL!
            }
            gym_dicts.append(gym_dict)

        return jsonify({'code': 200, 'message': 'Query successful', 'gyms': gym_dicts})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})

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
        return jsonify({'code': 400, 'message': 'Something went wrong.'})


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
            return jsonify({ 'code': 200, 'message': 'Password reset email sent successfully. Follow the link in the email within 10 minutes to reset your password.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})


####################
### TRAINING API ###
####################

@app.route('/api/training/save_log', methods=['GET', 'POST'])
def saveTraining():
    try:
        user = verify_token(request.headers.get('token'))
        if user is None:
            return jsonify({'code': 401, 'message': 'Training can only be saved while logged in.'})

        training = Training(
            notes = request.headers.get('notes'),
            is_public = request.headers.get('is_public'),
            date_created = datetime.date.today()
        )
        db.session.add(training)
        db.session.flush()

        for climb in request.headers.get('climbs'):
            send = Send(
                climb_id = climb['climb_id'],
                training_id = training.id,
                send_category = climb['send_category'],
                notes = climb['notes'],
                time_created = climb['time_created'],
                # TODO media url
            )
            db.session.add(send)

        db.session.commit()

        return jsonify({'code': 200, 'message': 'Your training log has been saved successfully.'})

    except:
        return jsonify({'code': 400, 'message': 'Something went wrong.'})
    
