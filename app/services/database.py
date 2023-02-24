from pymongo import MongoClient
import numpy as np
from scipy import stats

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
def getProjectMetrics(projectID):
    # Get the database
    db = getDatabase()

    # Get metrics
    initialProject = db["PROJECT"]
    projectMetrics = db["PROJECT_METRICS"]
    projectExpenditure = db["PROJECT_EXPENDITURE"]

    # Need to test once we have sample data to test from
    # Get methodology 
    methodology = list(initialProject.find( {"Methodology" : 1}, {"ProjectID" : projectID}))

    # Calculate averages
    expenditure = np.sum(np.array(list(projectExpenditure.find( {"ProjectID" : projectID}, {"Expenditure" : 1, "_id" : 0} ))))
    metricsMean = np.mean(np.array(list(projectMetrics.find( {"ProjectID" : projectID}, {"_id": 0, "Date" : 0, "Time" : 0 } ))), axis=0)
    onTrackMode = stats.mode(np.array(list(projectMetrics.find( {"ProjectID" : projectID}, {"On_Track" : 1} ))))

    # Concatenate list of metrics
    metrics = methodology + metricsMean + onTrackMode + expenditure
    return metrics
