from app import app, db
from flask import render_template, url_for, redirect, flash, jsonify, request
from app.forms import TitleForm, ContactForm, LoginForm, RegisterForm, PostForm
from app.models import Post, User
from flask_login import login_user, logout_user, login_required, current_user
import datetime


@app.route('/')
@app.route('/index')
@app.route('/index/<word>', methods=['GET'])
def index(word=''):

    return render_template('index.html', title='Home', word=word)


@app.route('/title', methods=['GET', 'POST'])
def title():
    form = TitleForm()

    # handle form submission
    if form.validate_on_submit():
        text = form.title.data

        return redirect(url_for('index', word=text))

    return render_template('form.html', title='Title', form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        flash(f'Thanks {form.name.data}, your message has been receive. We have sent a copy of the submission to {form.email.data}')

        return redirect(url_for('index'))

    return render_template('form.html', form=form, title='Contact Us')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in, redirect them
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('profile', username=current_user.username))

    form = LoginForm()

    if form.validate_on_submit():
        # query db for user info, and log them in if everything is valid
        user = User.query.filter_by(email=form.email.data).first()

        # if user doesn't exist, reload page and flash message
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Credentials.')
            return redirect(url_for('login'))

        # if user does exist, and credentials are valid
        login_user(user)
        flash('You have been logged in!')
        return redirect(url_for('profile', username=current_user.username))

    return render_template('form.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('profile', username=current_user.username))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            username = form.username.data,
            email = form.email.data,
            age = form.age.data,
            bio = form.bio.data
        )

        # include password to user
        user.set_password(form.password.data)

        # add and Commit
        db.session.add(user)
        db.session.commit()

        flash('You have been registered!')

        return redirect(url_for('login'))

    return render_template('form.html', form=form, title='Register')

@app.route('/profile')
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username=''):
    # If username is empty
    if not username:
        return redirect(url_for('login'))

    form = PostForm()

    person = User.query.filter_by(username=username).first()


    if form.validate_on_submit():
        tweet=form.tweet.data
        post = Post(user_id=current_user.id, tweet=tweet)

        # Commit to database
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('profile', username=username))

    return render_template('profile.html', title='Profile', person=person, form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


###################
#   API SECTION   #
###################

# Create an API that handles getting tweet information
@app.route('/api/posts/retrieve/', methods=['GET'])
def api_posts_retrieve():
    try:
        # Get variables passed into API
        username = request.args.get('username')
        month = request.args.get('month')

        if username and month:
            user = User.query.filter_by(username=username).first()
            posts = user.posts

            data = []

            for post in posts:
                if post.date_posted.month == int(month):
                    data.append({
                        'post_id' : post.post_id,
                        'user_id' : post.user_id,
                        'tweet' : post.tweet,
                        'date_posted' : post.date_posted
                    })

            return jsonify({'code' : 200, 'data' : data})


        if username:
            user = User.query.filter_by(username=username).first()
            posts = user.posts

            data = []
            for post in posts:
                data.append({
                    'post_id' : post.post_id,
                    'user_id' : post.user_id,
                    'tweet' : post.tweet,
                    'date_posted' : post.date_posted
                })

            return jsonify({'code' : 200, 'data' : data})

        return jsonify({ 'code' : 200, 'message' : 'Invalid params' })

    except:
        return jsonify({
            'message' : 'Error #1001: Something went wrong.',
            'code' : 1001
        })


# Create an API that handles posting tweets
@app.route('/api/posts/save/', methods=['GET', 'POST'])
def api_posts_save():
    try:
        # Get variables passed into API
        username = request.args.get('username')
        tweet = request.args.get('tweet')
        user = User.query.filter_by(username=username).first()

        if user:
            post = Post(user_id=user.id, tweet=tweet)

            db.session.add(post)
            db.session.commit()

            return jsonify({'code' : 200, 'message' : 'Tweet saved' })

        return jsonify({'code': 200, 'message' : 'Invalid params' })

    except:
        return jsonify({
            'message' : 'Error #1002: Something went wrong.',
            'code' : 1002
        })

# API to delete posts, take in post_id
@app.route('/api/posts/delete/', methods=['DELETE'])
def api_posts_delete():
    try:
        post_id = request.args.get('post_id')

        post = Post.query.get(int(post_id))

        db.session.delete(post)
        db.session.commit()

        return jsonify({ 'code' : 200, 'message' : 'Tweet deleted' })

    except:
        return jsonify({ 'code' : 1004, 'message' : 'Invalid params' })



# This API should accept info through headers securely, and pass back info of uer
@app.route('/api/users/retrieve/', methods=['GET', 'POST'])
def api_users_retrieve():
    try:
        # get headers first
        username = request.headers.get('username')
        API_KEY = request.headers.get('API_KEY')

        if API_KEY == 'secret':
            user = User.query.filter_by(username=username).first()

            info = {
                'first_name' : user.first_name,
                'last_name' : user.last_name,
                'age' : user.age,
                'username' : user.username,
                'email' : user.email
            }


            return jsonify({ 'code' : 200, 'data' : info })

        return jsonify({ 'code' : 200, 'message' : 'Invalid key' })


    except:
        return jsonify({
            'message' : 'Error #1003: Something went wrong.',
            'code' : 1003
        })
