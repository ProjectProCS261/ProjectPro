from pymongo import MongoClient
import numpy as np
from scipy import stats
from datetime import datetime
from team import getTeamSize
from project import getProject

# This function connects to the database
def getDatabase():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb+srv://Lucy:cs261@cluster0.qmtgd2o.mongodb.net/?retryWrites=true&w=majority"
 
   # Create a connection using MongoClient
   client = MongoClient(CONNECTION_STRING)
 
   return client['cs261']
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    db = getDatabase()

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

    start = datetime.strptime(projectData["StartDate"], "%Y-%m-%d").date()
    end = datetime.strptime(projectData["Deadline"], "%Y-%m-%d").date()
    days = abs(end-start).days
    months = days / (365/12)
    
    teamSize = getTeamSize(projectName, owner)
    
    # If no project metrics have been inputted yet, assume default values
    metricCount = projectMetrics.count_documents( {'projectID' : projectID} )
    if metricCount == 0:
        avgMorale = 5
        avgDiff = 5
        avgComm = 5
        avgProg = 5
        onTrack = 'On Schedule'
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
        avgMorale = metricsMean[0]['avgMorale']
        avgComm = metricsMean[0]['avgComm']
        avgDiff = metricsMean[0]['avgDiff']
        avgProg = metricsMean[0]['avgProg']
        onTrack = (projectMetrics.find( {'ProjectID' : projectID}, {'_id' : 0, 'On_Track' : 1} ).sort('$natural', -1).limit(1))[0]['On_Track']
    
    # Concatenate list of metrics
    metrics = [methodology,  months, teamSize, avgMorale, avgComm, avgDiff, avgProg, onTrack]
    return metrics