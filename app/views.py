from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from flask_login import login_user, LoginManager, logout_user, current_user, login_required, UserMixin
# import services.team, services.project, services.methodology, services.metrics, services.addingmetrics, services.database
import pymongo
# from models import User

import werkzeug
from datetime import date
from markupsafe import escape

from app import app

from datetime import datetime 

# This function connects to the database
def getDatabase():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb+srv://Lucy:cs261@cluster0.qmtgd2o.mongodb.net/?retryWrites=true&w=majority"
 
   # Create a connection using MongoClient
   client = pymongo.MongoClient(CONNECTION_STRING)
 
   return client['cs261']
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    db = getDatabase()

def insertTeam(projectID, owner):
    # Connect to database
    db = getDatabase()
    teams = db["TEAM"]
    userTeams = db["USER_TEAM"]

    # Create team
    teamID = teams.insert_one({
        'ProjectID' : projectID
    })

    # Add project owner to team
    userTeams.insert_one({
        'User_Email' : owner,
        'TeamID' : teamID.inserted_id
    })

# Inserts a new project into the database and returns project id
def insertProject(projectName, clientName, methodology, budget, owner, startDate, deadline):
    # Connect to database
    db = getDatabase()
    projects = db["PROJECT"]

    # Insert project
    projectID = projects.insert_one({
        'Project_Name' : projectName,
        'Client_Name' : clientName,
        'Methodology' : methodology,
        'Budget' : budget,
        'Owner_Email' : owner,
        'StartDate' : startDate,
        'Deadline' : deadline
    })

    # Create team for project
    insertTeam(projectID.inserted_id, owner)

    return projectID


# Gets information about a project returning a document e.g. {'_id' : ..., 'Project_Name' : ..., ...} otherwise returns None if project doesn't exist
def getProject(projectName, owner):
    # Connect to database
    db = getDatabase()
    projects = db["PROJECT"]

    # Get and return project
    project = projects.find_one( {'Project_Name' : projectName, 'Owner_Email' : owner} )
    return project

# Gets project ID
def getProjectID(projectName, owner):

    # Get project and return ID
    project = getProject(projectName, owner)
    return project['_id']

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb+srv://Brian:Kdh010315@cluster0.qmtgd2o.mongodb.net/test")
db = client["cs261"]
users = db["USER"]

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

# @app.route('/addproject')
# @login_required 
# def addProject():
#     return render_template('auth/addProject.html')

@app.route('/input')
# @login_required 
def input():
    return render_template('auth/input.html')

@app.route('/home')
@login_required
def home():
    # project_collection = db['PROJECT']
    # user_team_collection = db['USER_TEAM']
    # team_collection = db['TEAM']

    # print("\n current user email: {}\n".format(current_user.email))

    # # Get the email of the logged in user
    user_email = User.find_by_email(current_user.email)

    # print("user email: {}\n".format(user_email))

    # insertProject("pee", "Bank", "SCRUM", 100, "zainmobarik03@gmail.com", "10-01-2003", "10-01-2004")

    # # # 1. Query the user_team collection to get the team IDs that the user is associated with
    # user_teams = user_team_collection.find({'User_Email': current_user.email})

    # print("user teams: {}\n".format(user_teams))

    # # team_ids = [ut['TeamID'] for ut in user_teams]


    # # Initialize an empty list to store project IDs
    # project_ids = []

    # # Loop over each user_team document and extract the team ID
    # for user_team in user_teams:
    #     team_id = user_team['TeamID']

    #     print("teams ids: {}\n".format(team_id))
        
    #     # 2. Query the team collection to get the project IDs associated with this team ID
    #     team_projects = team_collection.find_one({'_id': team_id})

    #     print("teams projects: {}\n".format(team_projects))

    #     projIDs = [team_projects['ProjectID']]

    #     print("proj ids: {}\n".format(projIDs))

    #     project_ids.extend(projIDs)


    #     # 3. Query the project collection to get the project documents corresponding to those project IDs
    #     user_projects = project_collection.find({'_id': {'$in': project_ids}})

    # print("project ids: {}\n".format(project_ids))
    # print("user projects: {}\n".format(user_projects))

    # # 4. Extract the project_name field from each project document and display the list of project names
    # project_names = [p['Project_Name'] for p in user_projects]
    # print("------------------\n")
    # print(project_names)
    # print("------------------\n")

    projects = db['PROJECT'].find()

    return render_template('auth/home.html', name=current_user, projects=projects, user_email=user_email)

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

project_collection = db["PROJECT"]
user_team_collection = db["USER_TEAM"]
team_collection = db["TEAM"]

@app.route("/addProject", methods=["GET", "POST"])
def add_project():
    print("start")
    if request.method == "POST":
        print("POSTED")
        # Get the form data submitted by the user
        project_name = request.form["project_name"]
        client_name = request.form["client_name"]
        methodology = request.form["methodology"]
        budget = request.form["budget"]
        owner = request.form["owner"]
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        deadline = datetime.strptime(request.form["deadline"], "%Y-%m-%d")

        # Create a new project document with the form data
        project = {
            "Project_Name": project_name,
            "Client_Name": client_name,
            "Methodology": methodology,
            "Budget": budget,
            "Owner_Email": owner,
            "Start_Date": start_date,
            "Deadline": deadline
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

        # Get the email of the logged in user
        user_email = current_user.email

        print("USER EMAIL: {}\n".format(user_email))

        # Find the team ID associated with the logged in user
        user_team = user_team_collection.find_one({"User_Email": user_email})

        print("USER TEAM: {}\n".format(user_team))

        # Add the project ID to the team's list of project IDs
        team_id = user_team["TeamID"]
        print("TEAM ID: {}\n".format(team_id))
        team_collection.update_one(
            {"_id": team_id},
            {"$set": {"ProjectID": [projectID.inserted_id]}}
        )
        print("done")
        return redirect(url_for("home"))

    else:
        print("poooo")
        return render_template("auth/addProject.html")
