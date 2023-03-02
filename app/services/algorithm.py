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
    y = exampleData['lowMorale', 'tooDifficult', 'poorCommunication', 'outOfSpec'].values()

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
    overBudg = overBudget(projectName, owner)
    wrongMethod = wrongMethodology(projectName, owner) 
    # If over budget then increase probability of failure by how much over budget they are
    initProbOfFailure = initProbOfFailure * overBudg * wrongMethod
    onTrack = df['OnTrack'].values
    if onTrack == 'Behind Schedule':
        initProbOfFailure = initProbOfFailure * 1.26
    elif onTrack == 'Ahead of Schedule':
        initProbOfFailure = initProbOfFailure * 0.74
    # Print the confusion matrix and classification report
    #print(confusion_matrix(y_test, y_pred))
    #print(classification_report(y_test, y_pred))

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
    for expen in expenditures:
        ac += expen["Expenditure"]
    ev = budget * percentageDone
    cv = ev - ac
    if cv < 0:
        return 1 + (abs(cv) / budget)
    else:
        return 1

  
def wrongMethodology(projectName, owner):
    project = getProject(projectName, owner)
    methodology = project['Methodology']
    start = datetime.strptime(project["StartDate"], "%Y-%m-%d").date()
    end = datetime.strptime(project["Deadline"], "%Y-%m-%d").date()
    days = abs(end-start).days
    teamSize = getTeamSize(projectName, owner)
    badSize = False
    relativeSize = 0

    if methodology == "Waterfall" and teamSize < 15:
        badSize = True
        relativeSize = 15 - teamSize / 15
    elif methodology == "Agile" and teamSize > 11:
        badSize = True
        relativeSize = teamSize - 11 / teamSize
    elif methodology == "Lean" and teamSize > 7:
        badSize = True
        relativeSize = teamSize - 7 / teamSize
    elif methodology == "Scrum" and teamSize > 9:
        badSize = True
        relativeSize = teamSize - 9 / teamSize
    elif methodology == "Feature-Driven Development" and teamSize > 5:
        badSize = True
        relativeSize = teamSize - 5 / teamSize
    elif methodology == "Extreme-Programming" and teamSize > 12:
        badSize = True
        relativeSize = teamSize - 12 / teamSize
    
    if badSize:
        return 1 + relativeSize
    else:
        return 1
