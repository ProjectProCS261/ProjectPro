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
    
    onTrack = projectMetrics.find( {'ProjectID' : projectID}, {'_id' : 0, 'On_Track' : 1}).sort('$natural', -1).limit(1)
    
    # Concatenate list of metrics
    metrics = [methodology,  months, teamSize, metricsMean[0]['avgMorale'], metricsMean[0]['avgComm'], metricsMean[0]['avgDiff'], metricsMean[0]['avgProg'], onTrack[0]['On_Track']]
    return metrics