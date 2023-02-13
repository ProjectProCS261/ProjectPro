from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy

import datetime

db = SQLAlchemy()

# Bill calss for each different Bill that a user can select from.
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    email = db.Column(db.String(30))
    dateTime = db.Column(db.DateTime)

# List class to display all the Bills in a drop-down menu
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

    def __init__(self, title):
        self.title=title

# User class to store all the information about a user.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20))
    dateTime = db.Column(db.DateTime)

    def __init__(self, email, username, password):  
        self.username=username
        self.password=password
        self.email=email
        self.dateTime=datetime.datetime.now()

# Share class to store all the information about anyone that has been sent a bill. Used to see if a bill from a person is complete and how much they have to pay.
class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30))
    billTitle = db.Column(db.String(100))
    share = db.Column(db.Integer)
    complete = db.Column(db.Boolean)
    senderEmail = db.Column(db.String(30))
    dateTime = db.Column(db.DateTime)
    checkedPaid = db.Column(db.Boolean)
    checkedNew = db.Column(db.Boolean)
    total = db.Column(db.Integer)

    def __init__(self, email, billTitle, share, complete, senderEmail, dateTime, checkedPaid, checkedNew, total):  
        self.email=email
        self.billTitle=billTitle
        self.share=share
        self.complete=complete
        self.senderEmail=senderEmail
        self.dateTime=dateTime
        self.checkedPaid=checkedPaid
        self.checkedNew=checkedNew
        self.total=total

# Create some hard-coded users and Bills to use when testing the website.
def dbinit():
    # commit all the changes to the database file
    user_list = [
        User("fellypoo@gmail.com", "Felicia", "F-dog"), 
        User("pettypoo@gmail.com", "Petra", "P-dog")
        ]
    db.session.add_all(user_list)
    db.session.commit()

    lists = [List("Electricity")]
    db.session.add_all(lists)
    db.session.commit()
