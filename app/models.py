# from flask_login import UserMixin
# from werkzeug.security import check_password_hash
# import pymongo
# from pymongo import MongoClient

# client = pymongo.MongoClient("mongodb+srv://Brian:Kdh010315@cluster0.qmtgd2o.mongodb.net/test")
# db = client["cs261"]

# class User(UserMixin):
#     def __init__(self, email, password):
#         self.email = email
#         self.password = password

#     def get_id(self):
#         return str(self.email)

#     @staticmethod
#     def find_by_email(email):
#         user = db.users.find_one({'email': email})
#         if user:
#             return User(user['email'], user['password'])
#         return None

#     def check_password(self, password):
#         return check_password_hash(self.password, password)