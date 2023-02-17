from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for

app = Flask(__name__)
from app import views

# Secret Key for flask_login use
app.secret_key = "SecretVerySecret"