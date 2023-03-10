from .database import getDatabase
from .project import getProjectID

# Adds a user to a team
def addUserToTeam(userEmail, ownerEmail, projectName):
    # Connect to database
    db = getDatabase()
    userTeams = db["USER_TEAM"]
    teams = db["TEAM"]

    projectID = getProjectID(projectName, ownerEmail)
    teamID = teams.find_one( {'ProjectID' : [projectID]}, {'_id' : 1})['_id']
    # Add user to team 
    userTeams.insert_one({
        'User_Email' : userEmail,
        'TeamID' : teamID
    })
