import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from project import getProject, getExpenditures, getProjectID, getProjectMetrics, getTeamSize
import numpy as np
from datetime import datetime
import json

# Algorithm for calculating the probability of a project failing
def runAlg(projectName, owner):
    # Get project ID
    projectID = getProjectID(projectName, owner)

    # Load data to predict into a pandas DataFrame
    df = getProjectMetrics(projectID, projectName, owner)

    # Get example data
    f = open("sampledata.json")
    sampleData = json.load(f)
    exampleData = pd.to_csv(pd.read_json(sampleData))
    exampleData = pd.DataFrame(sampleData)

    # Split example data into features x and target y
    Xd = exampleData[['Methodology', 'Duration', 'GroupSize', 'MoraleRating', 'CommunicationRating', 'DifficultyRating']].to_numpy()
    yd = exampleData[['lowMorale','tooDifficult','poorCommunication']].to_numpy()

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(Xd, yd, test_size=0.2, random_state=0,shuffle = True)

    # Encode categorical data
    le = preprocessing.LabelEncoder()
    methodologies = X_train[:,0]
    methods = np.array(["Waterfall", "Scrum", "Agile", "Lean", "Feature-Driven", "Extreme Programming"])
    methodsEnc = (pd.get_dummies(methods)).values.tolist()
    methodsMatch = dict(zip(methods, methodsEnc))

    X_train_cat = [methodsMatch.get(item,item)  for item in methodologies]
    X_train_num = X_train[:,1:]
    X_train = np.column_stack((X_train_num, X_train_cat))

    morale = y_train[:,0]
    diff = y_train[:,1]
    comm = y_train[:,2]
    y_train = np.column_stack((le.fit_transform(morale), le.fit_transform(diff), le.fit_transform(comm)))

    # Train a linear regression model
    lr = LinearRegression(fit_intercept=False)
    lr.fit(X_train, y_train)

    # Predict on new data
    newData =  np.concatenate((df[1:6],methodsMatch.get(df[0]))).reshape(1,-1)
    yPred = lr.predict(newData)
    yPredNp = np.absolute(np.array(yPred))

    # Ensure probabilities aren't greater than 1
    lowMorale = 0.49 * min(yPredNp[0,0],1)
    tooDifficult = 0.72 * min(yPredNp[0,1],1)
    poorCommunication = 0.57 * min(yPredNp[0,2],1)

    # Calculate weighted average 
    initProbOfFailure =  (lowMorale + tooDifficult +  poorCommunication) / 1.78

    # Calculate additional probabilities
    onTrack = df[7]
    progress = df[6]
    overBudg = overBudget(projectName, owner)
    wrongMethod = wrongMethodology(projectName, owner)
    behind = behindSched(onTrack, progress)

    # Alter probability based on additional metrics
    initProbOfFailure = min(initProbOfFailure * overBudg * wrongMethod * behind,1)

    # Get actual probability of a project failing because of behing behind schedule and not making enough progress
    if behind >= 1:
        progressProb = behind - 1
    else:
        progressProb = behind
    # Get actual probability of a project going over budget
    if overBudg >= 1:
        budgetProb = overBudg - 1
    else:
        budgetProb = 0
    # Get actual probability of a project failing because of having the wrong methodology for the team size 
    if wrongMethod >= 1:
        methodTeamProb = wrongMethod - 1
    else:
        methodTeamProb = wrongMethod

    # Return list of probabilities
    return [initProbOfFailure, lowMorale, tooDifficult, poorCommunication, progressProb, budgetProb, methodTeamProb]

# Tests the algorithm using the test data and returns a score of accuracy (best possible score is 1)
def testAlg(model, X_test, y_test, methodsMatch):
    # Encode categorical data
    le = preprocessing.LabelEncoder()

    morale = y_test[:,0]
    diff = y_test[:,1]
    comm = y_test[:,2]
    y_test = np.column_stack((le.fit_transform(morale), le.fit_transform(diff), le.fit_transform(comm)))

    methodologiesTest = X_test[:,0]
    X_test_cat = [methodsMatch.get(item,item)  for item in methodologiesTest]
    X_test_num = X_test[:,1:]
    X_test = np.column_stack((X_test_num, X_test_cat))

    score = model.score(X_test, y_test)
    return score

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
    start = project["StartDate"]
    end = project["Deadline"]
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
        return min(1 + (abs(cv) / budget), 1.99)
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
    elif methodology == "Scrum" and teamSize > 10 or teamSize < 3:
        badSize = True
        if teamSize > 9:
            relativeSize = teamSize - 9 / teamSize
        else:
            relativeSize = (3 - teamSize) / 3
    elif methodology == "Feature-Driven" and teamSize > 5 or teamSize < 3:
        badSize = True
        if teamSize > 5:
            relativeSize = teamSize - 5 / teamSize
        else:
            relativeSize = (3 - teamSize) / 3
    elif methodology == "Extreme Programming" and teamSize > 12 or teamSize < 2:
        badSize = True
        if teamSize > 12:
            relativeSize = teamSize - 12 / teamSize
        else:
            relativeSize = (2 - teamSize) / 2
    
    if badSize:
        return 1 + relativeSize
    else:
        return 1
