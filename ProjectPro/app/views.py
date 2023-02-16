
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for

import werkzeug
from datetime import date
from markupsafe import escape

from app import app

# login_manager = LoginManager()
# login_manager.init_app(app)

@app.route('/')
def index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))  # Redirect to logged-in default page
    return render_template('nauth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # # Get data from mongoDB and check
        # userdata = User.query.filter_by(username=username).first()
        # if userdata is None:  # If User with entered username not in database, then return error.
        #     return jsonify(
        #         {
        #             "success": 0,
        #         }
        #     )
        # else:
        #     hashpass = userdata.password_hash
        #     check = werkzeug.security.check_password_hash(
        #         hashpass, password)  # Check Password
        #     if check:
        #         # Login
        #         login_user(userdata)
        #         return redirect(url_for('home'))
        #     else:
        #         return jsonify(
        #             {
        #                 "success": 0,
        #             }
        #         )

    return render_template('nauth/login.html')


@app.route('/register',  methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name')
        # Make sure username uniqueness doesn't get confusing.
        username = request.form.get('username').lower()
        password = request.form.get('password')
        if len(password) < 8:  # Secure Password
            return jsonify(
                {
                    "length": 0,
                }
            )
        password_hash = werkzeug.security.generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16)
        userdata = None
        if userdata is not None:  # If username is taken return error message
            return jsonify(
                {
                    "unique": 0,
                }
            )
        
        # Insert new User into db

        # Login
        # login_user(userdata)
        # return redirect(url_for('home'))
    return render_template('nauth/register.html')


# @app.route('/home')
# @login_required
# def home():
#     return redirect(url_for('main'))


# @ app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))


# @ login_manager.user_loader
# def load_user(user_id):
#     try:
#         # Change to MongoDB
#         return User.query.filter_by(id=user_id).first()
#     except User.DoesNotExist:
#         return None


# @ login_manager.unauthorized_handler
# def unauthorized_handler():
#     return redirect(url_for('index'))
