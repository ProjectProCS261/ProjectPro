from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from flask_login import login_user, LoginManager, logout_user, current_user, login_required, UserMixin

import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath('..app'))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from bson.objectid import ObjectId
from app.services.database import getDatabase
from app.services import project
from app.services.algorithm import runAlg

import werkzeug
from datetime import date, datetime, timedelta 

from app import app

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to the MongoDB database
db = getDatabase()
users = db["USER"]
project_collection = db["PROJECT"]
user_team_collection = db["USER_TEAM"]
team_collection = db["TEAM"]
metrics_collection = db["PROJECT_METRICS"]
expenditure_collection = db["PROJECT_EXPENDITURE"]

# User class for use by Flask-Login 
class User(UserMixin):
    def __init__(self, email):
        self.email = email

    def get_id(self):
        return str(self.email)

    @staticmethod
    def find_by_email(email):
        user = users.find_one({'email': email})
        if user:
            return User(user['email'])
        return None

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
            'passwordhash': password_hash,
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

def get_projects():
    user_email = current_user.email
    user_team = user_team_collection.find({"User_Email": user_email})
    projects = []
    inprogress = []
    
    for userT in user_team:
        team_id = userT["TeamID"]
        team = team_collection.find_one({"_id": team_id})
        project_id = team["ProjectID"][0]
        project = project_collection.find_one({"_id": project_id})
        if project["Completed"] == False:
            inprogress.append(project)
        projects.append(project)
    return projects, inprogress
    
@app.route('/home')
@login_required
def home():
    projects, inprogress = get_projects()
    pending = []
    day = datetime.today()
    for proj in inprogress:
        projectID = proj["_id"]
        print(projectID)
        print(proj["Project_Name"])
        entry = metrics_collection.find({"ProjectID": projectID, "User": current_user.email, "Date": {'$gte': (day - timedelta(days=7))}})
        size = 0
        for _ in entry:
            size+=1
        if size == 0:
            pending.append(proj)

    return render_template('auth/home.html', name=current_user, projects=projects, inprogress=inprogress, pending=pending)

@app.route("/addProject", methods=["GET", "POST"])
def add_project():
    if request.method == "POST":
        # Get the form data submitted by the user
        project_name = request.form["project_name"]
        client_name = request.form["client_name"]
        methodology = request.form["methodology"]
        budget = request.form["budget"]
        owner = current_user.email
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        deadline = datetime.strptime(request.form["deadline"], "%Y-%m-%d")

        # Create a new project document with the form data
        project = {
            "Project_Name": project_name,
            "Client_Name": client_name,
            "Methodology": methodology,
            "Budget": int(budget),
            "Owner_Email": owner,
            "Start_Date": start_date,
            "Deadline": deadline,
            "Completed": False
        }

        # Insert the project document into the projects collection
        projectID = project_collection.insert_one(project)

         # Create team
        teamID = team_collection.insert_one({
            'ProjectID' : [projectID.inserted_id]
        })

        # Add project owner to team
        user_team_collection.insert_one({
            'User_Email' : owner,
            'TeamID' : teamID.inserted_id
        })
        return redirect(url_for("home"))
    else:
        projects, inprogress = get_projects()
        return render_template("auth/addProject.html", name=current_user, inprogress=inprogress)


@app.route('/review', methods=["GET", "POST"])
@login_required
def review():
    if request.method == "POST":
        # Get the form data submitted by the user
        projectID = request.form["projectID"]
        owner = request.form["owner"]
        morale = float(request.form["morale"])
        difficulty = float(request.form["difficulty"])
        communication = float(request.form["communication"])
        today = datetime.today()
        user = current_user.email
        progress = float(request.form["progress"])
        status = "ontrack"
        if owner == "True":
            status = request.form["status"]
            expenses = "0"+request.form["expenses"]
            project_expenditure = {
                "ProjectID": projectID,
                "Expenditure": int(expenses),
                "Date": today
            }
            expenditure_collection.insert_one(project_expenditure)
            completion = request.form["completion"]
            if completion == "yes":
                print(1)
                project_collection.update_one({"_id": ObjectId(projectID)},{"$set": {"Completed": True}})

        # Create a new metrics entry with the form data
        project_metrics = {
            "ProjectID": ObjectId(projectID),
            "MoraleRating": morale,
            "DifficultyRating": difficulty,
            "CommunicationRating": communication,
            "Progress": progress,
            "On_Track": status,
            "Date": today,
            "User": user
        }
        metrics_collection.insert_one(project_metrics)

        return redirect(url_for('home'))

    else:
        projectID = request.args.get('projectID')
        current_project = project_collection.find_one({"_id": ObjectId(projectID)})
        owner = False
        if current_project['Owner_Email'] == current_user.email:
            owner = True
        projects, inprogress = get_projects()
        return render_template("auth/input.html", owner=owner, projectID=projectID, name=current_user, inprogress=inprogress)

@app.route('/projectdata', methods=["GET", "POST"])
@login_required 
def projectdata():
    if request.method == "POST":
        # Get the form data submitted by the user
        action = request.form["type"]
        teamID = request.form["TeamID"]
        projectID = request.form["ProjectID"]
        member = request.form["member"]
        if action == "add":
            new_user_team = {
                "User_Email": member,
                "TeamID": ObjectId(teamID)
            }
            user_team_collection.insert_one(new_user_team)
        else:
            user_team_collection.delete_one({"ProjectID": [ObjectId(projectID)], "User_Email": member})
        return redirect(url_for("projectdata", projectID=projectID))
    else:
        projectID = request.args.get('projectID')
        current_project = project_collection.find_one({"_id": ObjectId(projectID)})
        current_team = team_collection.find_one({"ProjectID": [ObjectId(projectID)]})
        members = user_team_collection.find({"TeamID": (current_team["_id"])})
        owner = False
        if current_project["Owner_Email"] == current_user.email:
            owner = True
        projects, inprogress = get_projects()

        costs = project.getExpenditures(current_project["Project_Name"], current_project["Owner_Email"])
        spending = (sum([i["Expenditure"] for i in costs]))
#        _,_,_, avgMorale, avgComm, avgDiff, avgProg, _ = project.getProjectMetrics(projectID, current_project["Project_Name"], current_project["Owner_Email"])     
        failure, avgMorale, avgDiff, avgComm, avgProg, _,_ = runAlg(current_project["Project_Name"], current_project["Owner_Email"])


        # results = runAlg(current_project["Project_Name"], current_project["Owner_Email"])
        # print(results)

        return render_template('auth/projectData.html', name=current_user, inprogress=inprogress, project=current_project, team=current_team, members=members, owner=owner
                               , avgMorale=avgMorale, avgComm=avgComm, avgDiff=avgDiff, avgProg=avgProg, failure=failure, spending=spending)

@login_manager.user_loader
def load_user(useremail):
    userdata = users.find_one({'email': useremail})
    if userdata:
        return User(userdata['email'])
    else:
        return None

@login_manager.unauthorized_handler 
def unauthorized_handler():
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(useremail):
    userdata = users.find_one({'email': useremail})
    if userdata:
        return User(userdata['email'])
    else:
        return None

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('index'))
