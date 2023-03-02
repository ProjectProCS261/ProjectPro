import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
from database import getProjectMetrics
from project import getProject, getExpenditures, getProjectID
from team import getTeamSize
import numpy as np
from datetime import datetime

def runAlg(projectName, owner):
    # Get project ID
    projectID = getProjectID(projectName, owner)
    # Load data to predict into a pandas DataFrame
    df = pd.read_csv(getProjectMetrics(projectID, projectName, owner))
    # Get example data
    exampleData = pd.to_csv(pd.read_json(sample))
    # Split example data into features x and target y
    # X should be 2D array
    X = exampleData[['Methodology', 'Budget', 'Duration', 'GroupSize', 'MoraleRating', 'DifficultyRating', 'CommunicationRating']].values()
    y = exampleData['lowMorale', 'tooDifficult', 'poorCommunication'].values()

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Train a logistic regression model
    clf = LogisticRegression(random_state=0)
    clf.fit(X_train, y_train)

    # Predict on the test set
    # y_pred = clf.predict(X_test)

    # Predict on given project metrics 
    newData = df['Methodology', 'MoraleRating', 'DifficultyRating', 'CommunicationRating'].values
    yPred = clf.predict_proba(newData)
    yPredNp = np.array(yPred)
    initProbOfFailure = np.sum(yPredNp)
    # Calculate additional probabilities
    onTrack = df['OnTrack'].values
    progress = df['avgProg'].values
    overBudg = overBudget(projectName, owner)
    wrongMethod = wrongMethodology(projectName, owner) 
    behind = behindSched(onTrack, progress)
    # Alter probability based on additional metrics
    initProbOfFailure = initProbOfFailure * overBudg * wrongMethod * behind

    # Print the confusion matrix and classification report
    #print(confusion_matrix(y_test, y_pred))
    #print(classification_report(y_test, y_pred))

# Calculates a probability based on how behind the project is and the average progress users are making
def behindSched(onTrack, progress):
    probOfFailure = 1
    # If the project is behind schedule but the team is making good progress on average then increase risk of failure by a reduced amount
    if onTrack == "Behind Schedule":
        if progress >= 7:
            probOfFailure = 1 + 0.26 * (1 - (progress / 10))
        else:
            probOfFailure = 1.26
    # If the project is on schedule the team is making bad progress on average then increase the risk of failure slightly
    elif onTrack == "On Schedule":
        if progress < 5:
            probOfFailure = 1 + 0.26 * (progress / 10)
    # If the project is ahead of schedule and the team is making good progress then decrease the risk of failure
    elif onTrack == "Ahead of Schedule":
        if progress >= 7:
            probOfFailure = 1 - (0.26 *  (progress / 10))
    return probOfFailure

            
# Calculates if a project is going to go over budget or not
def overBudget(projectName, owner):
    # Calculate total number of weeks 
    project = getProject(projectName, owner)
    start = datetime.strptime(project["StartDate"], "%Y-%m-%d").date()
    end = datetime.strptime(project["Deadline"], "%Y-%m-%d").date()
    days = abs(end-start).days
    currentDate = datetime.today().date()
    currentDays = abs(currentDate-start).days
    # Calculate percentage of project completed
    percentageDone = (days - currentDays) / days

    budget = project["Budget"]
    expenditures = getExpenditures(projectName, owner)
    ac = 0
    # Get total expenditure on project
    for expen in expenditures:
        ac += expen["Expenditure"]
    # Calculate how over budget the project is
    ev = budget * percentageDone
    cv = ev - ac
    if cv < 0:
        return 1 + (abs(cv) / budget)
    else:
        return 1

# Calculates if the team size is different to the recommended team size for the projects methodology
def wrongMethodology(projectName, owner):
    project = getProject(projectName, owner)
    methodology = project['Methodology']
    teamSize = getTeamSize(projectName, owner)
    badSize = False
    relativeSize = 1

    # Depending on methodology and reccommended team sizes, if a team size is smaller than or greater than it should be, alter probability based on how different
    # the team size is compared with the reccommended
    if methodology == "Waterfall" and teamSize < 15:
        badSize = True
        relativeSize = (15 - teamSize) / 15
    elif methodology == "Agile" and teamSize > 11 or teamSize < 5:
        badSize = True
        if teamSize > 11:
            relativeSize = (teamSize - 11) / teamSize
        else:
            relativeSize = (5 - teamSize) / 5
    elif methodology == "Lean" and teamSize > 7 or teamSize < 3:
        badSize = True
        if teamSize > 7:
            relativeSize = (teamSize - 7) / teamSize
        else:
            relativeSize = (3 - teamSize) / 3
    elif methodology == "Scrum" and teamSize > 9 or teamSize < 3:
        badSize = True
        if teamSize > 9:
            relativeSize = teamSize - 9 / teamSize
        else:
            relativeSize = (3 - teamSize) / 3
    elif methodology == "Feature-Driven Development" and teamSize > 5 or teamSize < 3:
        badSize = True
        if teamSize > 5:
            relativeSize = teamSize - 5 / teamSize
        else:
            relativeSize = (3 - teamSize) / 3
    elif methodology == "Extreme-Programming" and teamSize > 12 or teamSize < 2:
        badSize = True
        if teamSize > 12:
            relativeSize = teamSize - 12 / teamSize
        else:
            relativeSize = (2 - teamSize) / 2
    
    if badSize:
        return 1 + relativeSize
    else:
        return 1
