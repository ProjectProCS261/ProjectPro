from database import getDatabase
from project import getProjectID
# Creates team for a project after a project is created
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
    
# Adds a user to a team
def addUserToTeam(userEmail, ownerEmail, projectName):
    # Connect to database
    db = getDatabase()
    userTeams = db["USER_TEAM"]
    teams = db["TEAM"]

    projectID = getProjectID(projectName, ownerEmail)
    teamID = teams.find_one( {'ProjectID' : projectID}, {'_id' : 1})['_id']
    # Add user to team 
    userTeams.insert_one({
        'User_Email' : userEmail,
        'TeamID' : teamID
    })

def getTeamSize(projectName, ownerEmail):
    db = getDatabase()
    userTeams = db["USER_TEAM"]
    teams = db["TEAM"]
    projectID = getProjectID(projectName, ownerEmail)
    teamID = teams.find_one( {'ProjectID' : projectID}, {'_id' : 1})['_id']
    teamSize = userTeams.count_documents( {'TeamID' : teamID} )
    return teamSize