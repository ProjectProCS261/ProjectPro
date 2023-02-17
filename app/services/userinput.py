import pymongo
from datetime import datetime

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb+srv://Brian:Kdh010315@cluster0.qmtgd2o.mongodb.net/test")
db = client["cs261"]
collection = db["PROJECT_METRICS"]

# Continuously ask the user for ProjectID until a valid one is provided
while True:
    project_id = input("Enter ProjectID: ")
    if collection.find_one({"ProjectID": project_id}):
        break
    else:
        print("ProjectID not found. Please try again.")

# Get the user's input for the other attributes
morale_rating = int(input("Enter Morale Rating (0-10): "))
difficulty_rating = int(input("Enter Difficulty Rating (0-10): "))
communication_rating = int(input("Enter Communication Rating (0-10): "))
progress = int(input("Enter Progress (0-100): "))
on_track = input("On Track? (True/False): ") == "True"

# Get the current date and time
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Insert the data into the database
collection.insert_one({
    "ProjectID": project_id,
    "MoraleRating": morale_rating,
    "DifficultyRating": difficulty_rating,
    "CommunicationRating": communication_rating,
    "Progress": progress,
    "On_Track": on_track,
    "Timestamp": timestamp
})

# Confirm that the data has been inserted
print("Data successfully inserted.")

    
