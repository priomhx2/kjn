#Having CoreyMSchafers online tutorial, provided support in functionality
#Bootstrap
from flask import url_for, request, render_template, flash, redirect, abort
from directDecision import directDecision, db, bcrypt, mail
from directDecision.models import User, Post
from directDecision.forms import RegistrationForm, LoginForm, UpdateForm, PostForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_bootstrap import Bootstrap


#packages from python have been installed to retrieve current information for real time use
import os
import secrets
import datetime
import time


#spacy has been installed within python to support natural processing language tasks
import spacy
nlp = spacy.load('en')
from textblob import TextBlob
import pandas as pd
import numpy as np



Bootstrap(directDecision)

#routes for the homepage has been created to direct users to the main page. Users must login to access the page
@directDecision.route('/')
@login_required
def homepage():
    return render_template('homepage.html')

#allows user to access the blog page with all retrieval of all required information. Users must login to access the page
@directDecision.route("/userblog")
@login_required
def userblog():
    page = request.args.get('page', 1, type=int)

    # collects all posts created and stored from database
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('userblog.html', posts=posts)


#directs the user to the analysis html page which diaplays the analysis tools. Users must login to access the page
@directDecision.route("/analysis")
@login_required
def analysis():
    return render_template('analysis.html')

#directs the user to the about us html page. Users must login to access the page
@directDecision.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

@directDecision.route("/register", methods=['GET', 'POST'])
def register():
    # creates new user into database and authorises the access by matching the information on SQLite DB
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # bootstrap messages used to display message onto html page
        flash('Your account has been created! Please log in', 'success')

        # redirect the user back to the login page
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@directDecision.route("/login", methods=['GET', 'POST'])
def login():
    # query the database to ensure the user exists
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        # a conditional is created to verify if the username and password exists
        user =  User.query.filter_by(email = form.email.data).first()
        # compare database password to the password entered in the form
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('homepage'))

            # all credentials which aren't valid or stored on the database
        else:
            flash('Login Unsucessful. Please check username and email', 'danger')
    return render_template('login.html', title= 'Login', form=form)


@directDecision.route('/extract', methods=['GET', 'POST'])
def extract():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        document = nlp(rawtext)
        # Tokens are being created and analysed
        create_tokens = [token.text for token in document]
        #Word info of each word
        create_wordinfo= [ (token.text,token.is_stop) for token in document]
        # POS
        create_pos = [ (token.text,token.tag_,token.pos_,token.dep_) for token in document]
        # Sentiment
        blob = TextBlob(rawtext)
        blob_sentiment = blob.sentiment.polarity
        blob_subjectivity = blob.sentiment.subjectivity

    return render_template('analysis.html', create_tokens=create_tokens, create_wordinfo=create_wordinfo,create_pos=create_pos,blob_sentiment= blob_sentiment,blob_subjectivity=blob_subjectivity)

@directDecision.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@directDecision.route("/account",  methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()

        flash('Your account has been now been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title= 'Account', image_file =image_file, form=form)

# an instance of the post form is passed into the route
@directDecision.route("/post/new",  methods=['GET', 'POST'])
# GET and POST request is used to retireve and display content
@login_required
def new_post():

    form= PostForm()
    # handling function to ensure the post submited has been creating successfully
    if form.validate_on_submit():
        # sets variables to the post, which is then stored into the database
        post = Post(title= form.title.data, content=form.content.data, author=current_user)
# content is saved directly to the sql database
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')

# redirects the user to the blog html page
        return redirect(url_for('userblog'))
    return render_template('create_post.html', title= 'New Post', form=form, legend='New Post')

@directDecision.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@directDecision.route("/post/<int:post_id>/update",  methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    # if form is valid the post can be updated
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('userblog', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        # redirect route for a specific post using the post ID of current post
        # use legend to display post and will be changed according each account
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@directDecision.route("/post/<int:post_id>/delete", methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('userblog'))

# variable created for pagination which is post
@directDecision.route("/user/<string:username>")
def user_post(username):
    # pagination for each page
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='decisiondirect@gmail.com',recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
If you did not make this request then  ignore this email
'''
    mail.send(msg)

@directDecision.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@directDecision.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
