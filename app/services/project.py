from database import getDatabase
from team import insertTeam
from datetime import datetime 

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

    return projectID.inserted_id


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

# Add expenditure to database
def insertExpenditure(projectName, owner, expenditure, date):
    projectID = getProjectID(projectName, owner)
    db = getDatabase()
    expenditures = db["PROJECT_EXPENDITURE"]
    expenditures.insert_one({
        'ProjectID' : projectID,
        'Expenditure' : expenditure,
        'Date' : date
    })

# Returns all expenditures for a project
def getExpenditures(projectName, owner):
    projectID = getProjectID(projectName, owner)
    db = getDatabase()
    expenditures = db["PROJECT_EXPENDITURE"]
    allExpenditures = expenditures.find({ 'ProjectID' : projectID }, {'_id' : 0, 'Expenditure' : 1})
    return allExpenditures


# Add status to project once calculated
def insertStatus(projectName, owner, status):
    projectID = getProjectID(projectName, owner)
    db = getDatabase()
    statuses = db["PROJECT_STATUS"]
    statuses.insert_one({
        'ProjectID' : projectID,
        'Status' : status
    })

def insertMetrics(projectName, owner, morale, diff, comm, prog, onTrack, date):
    db = getDatabase()
    collection = db["PROJECT_METRICS"]
    projectID = getProjectID(projectName, owner)
    collection.insert_one({
        "ProjectID": projectID,
        "MoraleRating": morale,
        "DifficultyRating": diff,
        "CommunicationRating": comm,
        "Progress": prog,
        "On_Track": onTrack,
        "Date": date
    })
    