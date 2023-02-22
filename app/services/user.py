from database import getDatabase

# Still need to test once possible

# Insert user into the database given the user email and password hash
def insertUser(email, password):
    # Connect to database
    db = getDatabase()
    users = db["USER"]

    # Insert user into database
    users.insert_one({
        "Email" : email,
        "Password" : password
    })

# Get the password hash given a users email if email exists
def getPassword(email):
    # Connect to database
    db = getDatabase()
    users = db["USER"]

    # Check email exists in database
    emailCount = users.find( {'Email' : email}).limit(1).size()

    # If email does not exist, the password cannot be retrieved
    if emailCount == 0:
        return None
    
    # Otherwise get password hash 
    password = users.find_one( {"Email" : email}, {"Password" : 1, "_id" : 0})

    return password["Password"]

