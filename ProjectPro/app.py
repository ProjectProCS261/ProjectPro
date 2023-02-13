from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from schema import db, Bill, User, Share, List, dbinit
import datetime

app = Flask(__name__)
# Configuring database, making secret key and initialising database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'wybibqbwu87hs'
db.init_app(app)

# Initialising login details
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # The user_id is the primary key of our user table, so I use it to query all the users.
    return User.query.get(int(user_id))

# Code to reset all data in database.

resetdb = False
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()


#route to the index, the first page the user will come to when they arrive at my website.
@app.route('/')
def index():
    return render_template('login.html')

# Login route, passing in all the users for the HTML 
@app.route('/login')
def login():
    users = User.query.all()
    return render_template('login.html', users=users)

# Function to deal with the Login form.
@app.route('/login', methods=['POST'])
def login_post():
    # Get relevant data from form
    email = request.form.get('email')
    username = request.form.get("username")
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    uname = User.query.filter_by(username=username).first()

    # IF statement to check if a user exists in the database and to take the user's password and hash it. Compare the hashed password to the one in the database.
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for("login"))

    # Get the login time and update in User's database.
    loginTime = datetime.datetime.now()
    user.dateTime = loginTime
    db.session.commit()
    login_user(user)
    return redirect(url_for("bills"))

# Logout function with login decorator.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Function for register page
@app.route('/register')
def register():
    return render_template('register.html')

# Function to deal with the Registration form.
@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    # If a user with that email already exists redirect to register page and flash a message.
    if user:
        flash('Email address already exists')
        return redirect(url_for('register'))

    new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))
    