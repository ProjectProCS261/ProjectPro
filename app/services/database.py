from pymongo import MongoClient

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

