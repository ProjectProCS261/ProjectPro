from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from flask_login import login_user, LoginManager, logout_user, current_user, login_required, UserMixin

import pymongo

import werkzeug
from datetime import date
from markupsafe import escape

from app import app

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb+srv://Brian:Kdh010315@cluster0.qmtgd2o.mongodb.net/test")
db = client["cs261"]
users = db["USER"]

# User class for use by Flask-Login 
class User(UserMixin):
    def __init__(self, useremail):
        self.useremail = useremail

    def get_id(self):
        return self.useremail

@app.route('/')
def index():
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redirect to logged-in default page
    return render_template('nauth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    if request.method == 'POST':
        # Check if the username and password are valid
        userdata = users.find_one({'email': request.form['email'].lower()})
        if userdata:
            hashpass = userdata['passwordhash']
            check = werkzeug.security.check_password_hash(hashpass, request.form['password'])
            if check:
                loginUser = User(userdata['email'])
                # Login User
                login_user(loginUser)
                return redirect(url_for('home'))
            else:
                return render_template('nauth/login.html', error='Invalid username or password')

    return render_template('nauth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    if request.method == 'POST':
        # Check if the username already exists
        if users.find_one({'email': request.form['email'].lower()}):
            return render_template('nauth/register.html', error='Email already in use')
        
        # Check if the password and confirm password match
        if request.form['password'] != request.form['confirm_password']:
            return render_template('nauth/register.html', error='Passwords do not match')

        password_hash = werkzeug.security.generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=16)

        # Create a new user
        userdata = {
            'email': request.form['email'].lower(),
            'passwordhash': password_hash
        }
        users.insert_one(userdata)
        loginUser = User(userdata['email'])
        # Login User
        login_user(loginUser)

        return redirect(url_for('login'))

    return render_template('nauth/register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Logout User
    logout_user()
    return redirect(url_for('index'))

@app.route('/addproject')
@login_required 
def addProject():
    return render_template('auth/addProject.html')

@app.route('/input')
# @login_required 
def input():
    return render_template('auth/input.html')

@app.route('/home')
@login_required
def home():
    return render_template('auth/home.html')

@login_manager.user_loader
def load_user(useremail):
    userdata = users.find_one({'email': useremail})
    print(userdata)
    if userdata:
        return User(userdata['email'])
    else:
        return None

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('index'))