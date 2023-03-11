from .database import getDatabase

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
        'Start_Date' : startDate,
        'Deadline' : deadline
    })

    # Create team for project
    insertTeam(projectID.inserted_id, owner)

    return projectID.inserted_id

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
    allExpenditures = expenditures.find({'ProjectID':str(projectID)})
    return([i for i in allExpenditures])


# Add status to project once calculated
def insertStatus(projectName, owner, status):
    projectID = getProjectID(projectName, owner)
    db = getDatabase()
    statuses = db["PROJECT_STATUS"]
    statuses.insert_one({
        'ProjectID' : projectID,
        'Status' : status
    })

# Add a users metrics to database
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

# Get all metrics for a specific project once a project owner requests to calculate project risk
def getProjectMetrics(projectID, projectName, owner):
    # Get the database
    db = getDatabase()

    # Get metrics
    project = db["PROJECT"]
    projectMetrics = db["PROJECT_METRICS"]
    
    projectData = getProject(projectName, owner)

    # Get methodology 
    methodology = projectData['Methodology']

    start = projectData["Start_Date"]
    end = projectData["Deadline"]
    days = abs(end-start).days
    months = days / (365/12)
    
    teamSize = getTeamSize(projectName, owner)
    
     # If no project metrics have been inputted yet, assume default values
    metricCount = projectMetrics.count_documents( {'ProjectID' : projectID} )
    if metricCount == 0:
        onTrack = 'On Schedule'

        # Get all projectIDs in projectMetrics
        projectIDs = list(projectMetrics.find( {}, {'_id' : 0, 'ProjectID' : 1} ))
        numProjects = len(projectIDs)

        # If no projects have inputted any data into Project_Metrics yet, then assume average values
        if numProjects == 0:
            avgMorale = 5
            avgDiff = 5
            avgComm = 5
            avgProg = 5

        # Otherwise get the average of all week 1 metrics for all projects in Project_Metrics
        else:
            avgMorale = 0
            avgDiff = 0
            avgComm = 0
            avgProg = 0
            for pID in projectIDs:
                pMetric = projectMetrics.find( {'ProjectID' : pID['ProjectID']}, {'_id' : 0, 'ProjectID' : 0} ).sort('$natural', 1).limit(1)
                for m in pMetric:
                    avgMorale = avgMorale +  m['MoraleRating']
                    avgDiff = avgDiff + m['DifficultyRating']
                    avgComm =  avgComm + m['CommunicationRating']
                    avgProg = avgProg + m['Progress']
            avgMorale = avgMorale / numProjects
            avgDiff = avgDiff / numProjects
            avgComm = avgComm / numProjects
            avgProg = avgProg / numProjects

    else:
        # Calculate averages
        metricsMean = list(projectMetrics.aggregate([ {
                '$match': {'ProjectID' : projectID}
            }, {
                '$group' : { 
                '_id' : 0, 
                'avgMorale' : {'$avg': '$MoraleRating'}, 
                'avgComm' : {'$avg': '$CommunicationRating'}, 
                'avgDiff' : {'$avg': '$DifficultyRating'},
                'avgProg' : {'$avg' : '$Progress'}
            }}]))
        print(metricsMean)
        avgMorale = metricsMean[0]['avgMorale']
        avgComm = metricsMean[0]['avgComm']
        avgDiff = metricsMean[0]['avgDiff']
        avgProg = metricsMean[0]['avgProg']
        onTrack = (projectMetrics.find( {'ProjectID' : projectID}, {'_id' : 0, 'On_Track' : 1} ).sort('$natural', -1).limit(1))[0]['On_Track']
        
    # Concatenate list of metrics
    metrics = [methodology,  months, teamSize, avgMorale, avgComm, avgDiff, avgProg, onTrack]
    return metrics
    
# Gets the number of users in a team for a project
def getTeamSize(projectName, ownerEmail):
    db = getDatabase()
    userTeams = db["USER_TEAM"]
    teams = db["TEAM"]
    projectID = getProjectID(projectName, ownerEmail)
    teamID = teams.find_one( {'ProjectID' : [projectID]}, {'_id' : 1})['_id']
    teamSize = userTeams.count_documents( {'TeamID' : teamID} )
    return teamSize